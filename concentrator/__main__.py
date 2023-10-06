import sys

from concentrator.main import main as concentrator
from concentrator.load_test import main as load_test

PROGRAMS = {
    "concentrator": concentrator,
    "load_test": load_test,
}

if __name__ == "__main__":
    PROGRAMS.get(sys.argv[1] if len(sys.argv) > 1 else "concentrator", concentrator)()
