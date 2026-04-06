import datetime
import json
from pathlib import Path

import pytest

from fulcra_api.core import FulcraAPI

TOKEN_FILE = Path(__file__).parent.parent / ".fulcra_test_token.json"


def _load_token(fulcra: FulcraAPI) -> bool:
    """Load saved token. Returns True if a valid (non-expired) token was loaded."""
    if not TOKEN_FILE.exists():
        return False
    data = json.loads(TOKEN_FILE.read_text())
    expiration = datetime.datetime.fromisoformat(data["expiration"])
    if expiration <= datetime.datetime.now():
        return False
    fulcra.set_cached_access_token(data["access_token"])
    fulcra.set_cached_access_token_expiration(expiration)
    if data.get("refresh_token"):
        fulcra.set_cached_refresh_token(data["refresh_token"])
    return True


def _save_token(fulcra: FulcraAPI):
    """Persist the current token to disk."""
    data = {
        "access_token": fulcra.get_cached_access_token(),
        "expiration": fulcra.get_cached_access_token_expiration().isoformat(),
        "refresh_token": fulcra.get_cached_refresh_token(),
    }
    TOKEN_FILE.write_text(json.dumps(data, indent=2))


@pytest.fixture(scope="session")
def fulcra_client() -> FulcraAPI:
    fulcra = FulcraAPI()
    if not _load_token(fulcra):
        fulcra.authorize()
        _save_token(fulcra)
    return fulcra
