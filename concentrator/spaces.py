import json
from pathlib import Path
from typing import Optional, Dict, Any

from concentrator.client import Client


class Spaces:
    def __init__(self, client: Client, spaces_file: Path) -> None:
        self.client = client
        self.spaces_file = spaces_file
        self._spaces_index = {}

    def refresh(self) -> None:
        spaces = self.client.list_parkinglot_spaces()["spaces"]
        self._spaces_index = {s["internal_id"]: s for s in spaces}
        with self.spaces_file.open("w") as f:
            json.dump(self._spaces_index, f, indent=4)

    def get(self, id: int) -> Optional[Dict[str, Any]]:
        if space := self._spaces_index.get(id):
            return space
        self.refresh()
        return self._spaces_index.get(id)


if __name__ == "__main__":
    from concentrator.configs import create_configs
    from concentrator.client import TokenManager

    configs = create_configs()
    client = Client(
        token_manager=TokenManager(
            configs.configs_dir.joinpath(configs.client.token_file)
        ),
        client_config=configs.client,
    )
    spaces = Spaces(
        client=client,
        spaces_file=configs.configs_dir.joinpath("spaces.json"),
    )

    print(spaces.get(0))
