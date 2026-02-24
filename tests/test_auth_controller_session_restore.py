"""
tests/test_auth_controller_session_restore.py

Covers AuthController session restoration via token_storage + jwt_handler,
and Sentry user scope restore/reset behavior.

Non-regression: assertions match current implementation:
- get_logged_in_user() sets Sentry user with {"id": str(id), "department": dept}
  (no username restoration)
"""

import pytest
from app.controllers.auth_controller import AuthController
from app.repositories.employee_repository import EmployeeRepository


@pytest.fixture
def auth_ctrl(db_session):
    """AuthController wired with a real repository (DB not used in these tests)."""
    return AuthController(EmployeeRepository(db_session))


def test_get_logged_in_user_no_token(monkeypatch, auth_ctrl):
    """If no token exists, return None and do not touch current_user_data."""
    from app.controllers import auth_controller as auth_mod

    monkeypatch.setattr(auth_mod, "get_token", lambda: None)

    out = auth_ctrl.get_logged_in_user()
    assert out is None
    assert auth_ctrl.current_user_data is None


def test_get_logged_in_user_valid_token_restores_sentry(monkeypatch, auth_ctrl):
    """
    Valid token -> returns payload, sets current_user_data,
    and restores Sentry user with id coerced to string.
    """
    from app.controllers import auth_controller as auth_mod

    sentry = {"value": None}

    def _fake_set_user(value):
        sentry["value"] = value

    monkeypatch.setattr(auth_mod, "get_token", lambda: "dummy.jwt.token")
    monkeypatch.setattr(
        auth_mod,
        "decode_token",
        lambda _t: {"id": 1, "department": "SALES"},
    )
    monkeypatch.setattr(auth_mod.sentry_sdk, "set_user", _fake_set_user)

    payload = auth_ctrl.get_logged_in_user()
    assert payload == {"id": 1, "department": "SALES"}
    assert auth_ctrl.current_user_data == {"id": 1, "department": "SALES"}

    # Non-regression: implementation sets string id and does not include username
    assert sentry["value"] == {"id": "1", "department": "SALES"}


def test_get_logged_in_user_invalid_token_deletes_token(monkeypatch, auth_ctrl):
    """Invalid/expired token -> delete_token is called and None is returned."""
    from app.controllers import auth_controller as auth_mod

    deleted = {"called": False}

    def _fake_delete():
        deleted["called"] = True

    monkeypatch.setattr(auth_mod, "get_token", lambda: "dummy.jwt.token")
    monkeypatch.setattr(auth_mod, "decode_token", lambda _t: None)
    monkeypatch.setattr(auth_mod, "delete_token", _fake_delete)

    payload = auth_ctrl.get_logged_in_user()
    assert payload is None
    assert deleted["called"] is True


def test_logout_clears_sentry_and_session(monkeypatch, auth_ctrl):
    """logout() clears token, clears Sentry user, and resets current_user_data."""
    from app.controllers import auth_controller as auth_mod

    deleted = {"called": False}
    sentry = {"value": "not-none"}

    def _fake_delete():
        deleted["called"] = True

    def _fake_set_user(value):
        sentry["value"] = value

    auth_ctrl.current_user_data = {"id": 99, "department": "MANAGEMENT"}

    monkeypatch.setattr(auth_mod, "delete_token", _fake_delete)
    monkeypatch.setattr(auth_mod.sentry_sdk, "set_user", _fake_set_user)

    auth_ctrl.logout()

    assert deleted["called"] is True
    assert sentry["value"] is None
    assert auth_ctrl.current_user_data is None