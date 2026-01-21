"""Tests for authentication functionality."""

from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@asynccontextmanager
async def _noop_session_manager():
    """Disable MCP session manager startup for tests."""
    yield


@pytest.fixture
def temp_data_dirs(tmp_path):
    """Create temporary data directories for test runs."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    inbox_dir = data_dir / "inbox"
    inbox_dir.mkdir()
    atlas_dir = data_dir / "atlas"
    atlas_dir.mkdir()
    meta_dir = data_dir / ".meta"
    meta_dir.mkdir()
    state_dir = data_dir / ".gardener"
    state_db = state_dir / "state.db"

    return {
        "data_dir": data_dir,
        "inbox_dir": inbox_dir,
        "atlas_dir": atlas_dir,
        "meta_dir": meta_dir,
        "state_dir": state_dir,
        "state_db": state_db,
    }


class TestAuthDisabled:
    """Test that auth is disabled by default."""

    @pytest.fixture
    def client(self, temp_data_dirs):
        """Create test client with auth disabled (default)."""
        with (
            patch("config.DATA_DIR", temp_data_dirs["data_dir"]),
            patch("config.INBOX_DIR", temp_data_dirs["inbox_dir"]),
            patch("config.ATLAS_DIR", temp_data_dirs["atlas_dir"]),
            patch("config.META_DIR", temp_data_dirs["meta_dir"]),
            patch("config.STATE_DIR", temp_data_dirs["state_dir"]),
            patch("config.STATE_DB", temp_data_dirs["state_db"]),
            patch("config.AUTH_ENABLED", False),
            patch("config.AUTH_TOKEN", ""),
            patch("main.DATA_DIR", temp_data_dirs["data_dir"]),
            patch("main.INBOX_DIR", temp_data_dirs["inbox_dir"]),
            patch("main.ATLAS_DIR", temp_data_dirs["atlas_dir"]),
            patch("main.AUTH_ENABLED", False),
            patch("main.AUTH_TOKEN", ""),
        ):
            from main import app, mcp

            with patch.object(mcp.session_manager, "run", _noop_session_manager):
                with TestClient(app) as client:
                    yield client

    def test_status_endpoint_accessible_without_auth(self, client):
        """Status endpoint should be accessible when auth is disabled."""
        response = client.get("/api/status")
        assert response.status_code == 200

    def test_no_auth_header_required(self, client):
        """No auth header should be required when auth is disabled."""
        response = client.get("/api/status")
        assert response.status_code == 200
        assert "authentication" not in response.text.lower()


class TestAuthEnabled:
    """Test authentication when enabled."""

    @pytest.fixture
    def client_with_auth(self, temp_data_dirs):
        """Create test client with auth enabled."""
        test_token = "test-secret-token-12345"
        with (
            patch("config.DATA_DIR", temp_data_dirs["data_dir"]),
            patch("config.INBOX_DIR", temp_data_dirs["inbox_dir"]),
            patch("config.ATLAS_DIR", temp_data_dirs["atlas_dir"]),
            patch("config.META_DIR", temp_data_dirs["meta_dir"]),
            patch("config.STATE_DIR", temp_data_dirs["state_dir"]),
            patch("config.STATE_DB", temp_data_dirs["state_db"]),
            patch("config.AUTH_ENABLED", True),
            patch("config.AUTH_TOKEN", test_token),
            patch("main.DATA_DIR", temp_data_dirs["data_dir"]),
            patch("main.INBOX_DIR", temp_data_dirs["inbox_dir"]),
            patch("main.ATLAS_DIR", temp_data_dirs["atlas_dir"]),
            patch("main.AUTH_ENABLED", True),
            patch("main.AUTH_TOKEN", test_token),
        ):
            from main import app, mcp

            with patch.object(mcp.session_manager, "run", _noop_session_manager):
                with TestClient(app) as client:
                    yield client, test_token

    def test_returns_401_without_token(self, client_with_auth):
        """Should return 401 when no token provided."""
        client, _ = client_with_auth
        response = client.get("/api/status")
        assert response.status_code == 401
        assert "authentication required" in response.json()["detail"].lower()

    def test_returns_403_with_invalid_token(self, client_with_auth):
        """Should return 403 when token is invalid."""
        client, _ = client_with_auth
        response = client.get(
            "/api/status", headers={"Authorization": "Bearer wrong-token"}
        )
        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()

    def test_accepts_bearer_token(self, client_with_auth):
        """Should accept valid Bearer token."""
        client, token = client_with_auth
        response = client.get(
            "/api/status", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_accepts_x_auth_token_header(self, client_with_auth):
        """Should accept valid X-Auth-Token header."""
        client, token = client_with_auth
        response = client.get("/api/status", headers={"X-Auth-Token": token})
        assert response.status_code == 200

    def test_bearer_token_case_insensitive(self, client_with_auth):
        """Should accept 'bearer' in any case."""
        client, token = client_with_auth
        response = client.get(
            "/api/status", headers={"Authorization": f"BEARER {token}"}
        )
        assert response.status_code == 200

    def test_protects_mcp_endpoints(self, client_with_auth):
        """Should protect MCP endpoints."""
        client, token = client_with_auth
        # Without token
        response = client.get("/mcp/")
        assert response.status_code == 401

        # With invalid token
        response = client.get("/mcp/", headers={"Authorization": "Bearer wrong"})
        assert response.status_code == 403


class TestVerifyAuthToken:
    """Test the verify_auth_token dependency directly."""

    @pytest.fixture
    def verify_auth(self):
        """Import verify_auth_token with mocked config."""
        test_token = "test-token"
        with (
            patch("main.AUTH_ENABLED", True),
            patch("main.AUTH_TOKEN", test_token),
        ):
            from main import verify_auth_token

            yield verify_auth_token, test_token

    @pytest.mark.asyncio
    async def test_passes_with_valid_bearer_token(self, verify_auth):
        """Should pass with valid Bearer token."""
        verify_fn, token = verify_auth
        # Should not raise
        await verify_fn(authorization=f"Bearer {token}", x_auth_token=None)

    @pytest.mark.asyncio
    async def test_passes_with_valid_x_auth_token(self, verify_auth):
        """Should pass with valid X-Auth-Token."""
        verify_fn, token = verify_auth
        # Should not raise
        await verify_fn(authorization=None, x_auth_token=token)

    @pytest.mark.asyncio
    async def test_raises_401_without_token(self, verify_auth):
        """Should raise 401 when no token provided."""
        from fastapi import HTTPException

        verify_fn, _ = verify_auth
        with pytest.raises(HTTPException) as exc:
            await verify_fn(authorization=None, x_auth_token=None)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_raises_403_with_invalid_token(self, verify_auth):
        """Should raise 403 when token is invalid."""
        from fastapi import HTTPException

        verify_fn, _ = verify_auth
        with pytest.raises(HTTPException) as exc:
            await verify_fn(authorization="Bearer wrong", x_auth_token=None)
        assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_noop_when_auth_disabled(self):
        """Should be a no-op when auth is disabled."""
        with (
            patch("main.AUTH_ENABLED", False),
            patch("main.AUTH_TOKEN", ""),
        ):
            from main import verify_auth_token

            # Should not raise even without any token
            await verify_auth_token(authorization=None, x_auth_token=None)
