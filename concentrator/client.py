from pathlib import Path
import time
from typing import Any, Dict, Optional
from pydantic import BaseModel

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from concentrator.configs import ClientConfig, create_configs


class Token(BaseModel):
    access_token: str = ""
    expires_in: int = -1
    token_type: str = "Bearer"
    expires_at: float = -1


class TokenManager:
    def __init__(self, token_path: Path) -> None:
        self.token_path = token_path
        self._token: Optional[Token] = None

    @property
    def token(self) -> Token:
        if self._token:
            return self._token
        with self.token_path.open("r") as f:
            self._token = Token.model_validate_json(f.read())
            return self._token

    @token.setter
    def token(self, value: Dict[str, Any]) -> None:
        self._token = Token.model_validate(value)
        with self.token_path.open("w") as f:
            f.write(self._token.model_dump_json(indent=4))

    def is_expired(self) -> bool:
        return self.token.access_token == "" or time.time() >= self.token.expires_at


class Client:
    def __init__(
        self,
        token_manager: TokenManager,
        client_config: ClientConfig,
    ) -> None:
        self.token_manager = token_manager
        self.config = client_config
        self._session = OAuth2Session(
            client=BackendApplicationClient(
                client_id=self.config.client_id,
                scope=[
                    "smartparking/bookings:read",
                    "smartparking/bookings:write",
                ],
            ),
            token=self.token_manager.token.model_dump(),
        )

    @property
    def session(self) -> OAuth2Session:
        self._refresh()
        return self._session

    def _refresh(self) -> None:
        if not self.token_manager.is_expired():
            return
        self.token_manager.token = self._session.fetch_token(
            token_url=self.config.token_url,
            client_secret=self.config.client_secret,
        )
        self._session.token = self.token_manager.token

    def list_parkinglot_spaces(self) -> Dict[str, Any]:
        return self.session.get(
            f"{self.config.api_url}/parkinglots/{self.config.parkinglot_id}/spaces"
        ).json()

    def take_space(self, space_id: str) -> None:
        self.session.put(
            f"{self.config.api_url}/parkinglots/{self.config.parkinglot_id}/spaces/{space_id}/take"
        )

    def release_space(self, space_id: str) -> None:
        self.session.put(
            f"{self.config.api_url}/parkinglots/{self.config.parkinglot_id}/spaces/{space_id}/realease"
        )

    def update_space_state(self, space_id: str, taken: bool) -> None:
        action = self.take_space if taken else self.release_space
        action(space_id)


if __name__ == "__main__":
    from concentrator.configs import create_configs

    configs = create_configs()
    client = Client(
        token_manager=TokenManager(
            configs.configs_dir.joinpath(configs.client.token_file)
        ),
        client_config=configs.client,
    )
    print(client.list_parkinglot_spaces())
