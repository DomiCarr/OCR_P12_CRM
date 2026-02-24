"""
tests/test_repository_and_decorators_coverage.py

Covers:
- BaseRepository rollback paths (add/update/delete)
- require_auth decorator user_data resolution paths

Non-regression: require_auth is used WITHOUT parameters (it's not a factory).
Non-regression: user_data is provided via kwargs / controller session / token,
not via positional args (current implementation doesn't support that).
"""

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models.client import Client
from app.repositories.base_repository import BaseRepository
from app.utils.decorators import require_auth


class _DummyAuthCtrl:
    """Minimal auth controller stub used by require_auth fallback logic."""

    def __init__(self):
        self.current_user_data = None


class _DummyController:
    """Controller-like object holding auth_controller for @require_auth."""

    def __init__(self, auth_ctrl):
        self.auth_controller = auth_ctrl

    @require_auth
    def action(self, *args, user_data=None, **kwargs):
        """Return resolved user_data so tests can assert injection works."""
        return user_data

    @require_auth
    def action_with_arg(self, value, *args, user_data=None, **kwargs):
        """Ensures decorator doesn't break positional parameters."""
        return {"value": value, "user_data": user_data}


def _make_valid_client(index: int = 1) -> Client:
    """
    Create a Client respecting DB constraints.
    Adjust here if your model has additional NOT NULL constraints.
    """
    return Client(
        full_name=f"Client {index}",
        email=f"client{index}@example.com",
        phone=f"06000000{index}",
        company_name=f"Company {index}",
    )


def test_base_repository_update_rollback_on_sqlalchemy_error(db_session):
    """If commit fails during update, the session should rollback and raise."""
    repo = BaseRepository(db_session, Client)
    client = repo.add(_make_valid_client(1))

    rolled = {"called": False}

    def _fake_rollback():
        rolled["called"] = True

    def _fake_commit():
        raise SQLAlchemyError("boom")

    db_session.rollback = _fake_rollback
    db_session.commit = _fake_commit

    with pytest.raises(SQLAlchemyError):
        repo.update(client.id, {"phone": "0699999999"})

    assert rolled["called"] is True


def test_base_repository_delete_rollback_on_sqlalchemy_error(db_session):
    """If commit fails during delete, the session should rollback and raise."""
    repo = BaseRepository(db_session, Client)
    client = repo.add(_make_valid_client(2))

    rolled = {"called": False}

    def _fake_rollback():
        rolled["called"] = True

    def _fake_commit():
        raise SQLAlchemyError("boom")

    db_session.rollback = _fake_rollback
    db_session.commit = _fake_commit

    with pytest.raises(SQLAlchemyError):
        repo.delete(client)

    assert rolled["called"] is True


def test_require_auth_accepts_user_data_from_kwargs():
    """user_data provided explicitly via kwargs is passed through unchanged."""
    auth = _DummyAuthCtrl()
    ctrl = _DummyController(auth)

    user = {"id": 1, "department": "SALES"}
    out = ctrl.action(user_data=user)
    assert out == user


def test_require_auth_uses_controller_current_user_data():
    """If no explicit user_data, decorator falls back to auth_controller.current_user_data."""
    auth = _DummyAuthCtrl()
    auth.current_user_data = {"id": 3, "department": "MANAGEMENT"}
    ctrl = _DummyController(auth)

    out = ctrl.action()
    assert out == {"id": 3, "department": "MANAGEMENT"}


def test_require_auth_uses_token_payload(monkeypatch):
    """If no user_data anywhere, decorator uses token -> decode_token payload."""
    from app.utils import decorators as dec_mod

    auth = _DummyAuthCtrl()
    ctrl = _DummyController(auth)

    monkeypatch.setattr(dec_mod, "get_token", lambda: "dummy.jwt.token")
    monkeypatch.setattr(dec_mod, "decode_token", lambda _t: {"id": 7, "department": "SALES"})

    out = ctrl.action()
    assert out == {"id": 7, "department": "SALES"}


def test_require_auth_denies_when_no_user_and_no_token(monkeypatch):
    """If no user_data and no token, decorator returns None."""
    from app.utils import decorators as dec_mod

    auth = _DummyAuthCtrl()
    ctrl = _DummyController(auth)

    monkeypatch.setattr(dec_mod, "get_token", lambda: None)

    out = ctrl.action()
    assert out is None


def test_require_auth_denies_when_token_invalid(monkeypatch):
    """If token exists but decode_token returns None, decorator returns None."""
    from app.utils import decorators as dec_mod

    auth = _DummyAuthCtrl()
    ctrl = _DummyController(auth)

    monkeypatch.setattr(dec_mod, "get_token", lambda: "dummy.jwt.token")
    monkeypatch.setattr(dec_mod, "decode_token", lambda _t: None)

    out = ctrl.action()
    assert out is None


def test_require_auth_does_not_break_positional_args():
    """Decorator must preserve normal positional args and inject user_data."""
    auth = _DummyAuthCtrl()
    ctrl = _DummyController(auth)

    user = {"id": 10, "department": "SALES"}
    out = ctrl.action_with_arg("hello", user_data=user)

    assert out["value"] == "hello"
    assert out["user_data"] == user