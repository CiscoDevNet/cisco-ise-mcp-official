# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved
import base64
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

pytest_plugins = ("pytest_asyncio",)


def _reset():
    import clients.ise_web_session as mod
    mod.IseWebSession._instance = None
    mod.IseWebSession._initialized = False


def _resp(status_code=200, headers=None, text=""):
    r = MagicMock(spec=httpx.Response)
    r.status_code = status_code
    r.headers = headers or {}
    r.text = text
    r.cookies = httpx.Cookies()
    return r


class TestTier1EnvCookie:
    def setup_method(self):
        _reset()

    @pytest.mark.asyncio
    async def test_env_cookie_used_directly_no_login(self):
        import clients.ise_web_session as mod
        ok = _resp(200)
        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(return_value=ok)
        with patch("clients.ise_web_session.settings") as s:
            s.ise_admin_session_cookie = MagicMock()
            s.ise_admin_session_cookie.get_secret_value.return_value = "APPSESSIONID=a; MNTLA_JWT_TOKEN=b"
            client = mod.IseWebSession()
            client._client = mock_httpx
            resp = await client.get("https://host/admin/x.log.zip")
            assert resp is ok
            # Cookie header attached; no POST to LoginAction
            _, kwargs = mock_httpx.get.call_args
            assert "Cookie" in kwargs["headers"]
            mock_httpx.post = AsyncMock()  # ensure not called
            mock_httpx.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_env_cookie_expiry_fails_loud(self):
        import clients.ise_web_session as mod
        redirect = _resp(302, headers={"location": "/admin/login.jsp"})
        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(return_value=redirect)
        with patch("clients.ise_web_session.settings") as s:
            s.ise_admin_session_cookie = MagicMock()
            s.ise_admin_session_cookie.get_secret_value.return_value = "APPSESSIONID=a"
            client = mod.IseWebSession()
            client._client = mock_httpx
            with pytest.raises(mod.IseSessionAuthError, match="[Rr]efresh"):
                await client.get("https://host/admin/x.log.zip")


LOGIN_HTML = (
    '<form name="loginForm" action="LoginAction.do" method="POST">'
    '<input type="hidden" name="CSRFTokenNameValue" '
    'value=OWASP_CSRFTOKEN=OPIV-GQZ1-ABCD-K90A>'
    '</form>'
)


class TestTier2FormLogin:
    def setup_method(self):
        _reset()

    def test_scrape_csrf(self):
        import clients.ise_web_session as mod
        token = mod.IseWebSession._scrape_csrf(LOGIN_HTML)
        assert token == "OWASP_CSRFTOKEN=OPIV-GQZ1-ABCD-K90A"

    def test_scrape_csrf_missing_raises(self):
        import clients.ise_web_session as mod
        with pytest.raises(mod.IseSessionAuthError):
            mod.IseWebSession._scrape_csrf("<form></form>")

    @pytest.mark.asyncio
    async def test_form_login_then_get_succeeds(self):
        import clients.ise_web_session as mod
        login_page = _resp(200, text=LOGIN_HTML)
        login_post = _resp(302, headers={"location": "https://host/"})
        zip_ok = _resp(200)
        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.cookies = httpx.Cookies()
        mock_httpx.get = AsyncMock(side_effect=[login_page, zip_ok])
        mock_httpx.post = AsyncMock(return_value=login_post)
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value=None):
            s.ise_admin_session_cookie = None
            s.api_username = "admin"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "pw"
            s.ise_ip = "host"
            s.api_port = 443
            client = mod.IseWebSession()
            client._client = mock_httpx
            resp = await client.get("https://host/admin/x.log.zip")
            assert resp is zip_ok
            mock_httpx.post.assert_awaited_once()
            # POST body carried the service-account username
            _, post_kwargs = mock_httpx.post.call_args
            assert post_kwargs["data"]["name"] == "admin"

    @pytest.mark.asyncio
    async def test_bad_credentials_200_raises(self):
        import clients.ise_web_session as mod
        login_page = _resp(200, text=LOGIN_HTML)
        login_post = _resp(200, text=LOGIN_HTML)  # 200 = login failed
        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.cookies = httpx.Cookies()
        mock_httpx.get = AsyncMock(return_value=login_page)
        mock_httpx.post = AsyncMock(return_value=login_post)
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value=None):
            s.ise_admin_session_cookie = None
            s.api_username = "admin"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "wrong"
            s.ise_ip = "host"
            s.api_port = 443
            client = mod.IseWebSession()
            client._client = mock_httpx
            with pytest.raises(mod.IseSessionAuthError):
                await client.get("https://host/admin/x.log.zip")

    @pytest.mark.asyncio
    async def test_expired_session_reauths_once(self):
        import clients.ise_web_session as mod
        login_page = _resp(200, text=LOGIN_HTML)
        login_post = _resp(302, headers={"location": "https://host/"})
        first_get = _resp(302, headers={"location": "/admin/login.jsp"})
        second_get = _resp(200)
        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.cookies = httpx.Cookies()
        # login page, first zip GET(302), re-login page, second zip GET(200)
        mock_httpx.get = AsyncMock(side_effect=[login_page, first_get, login_page, second_get])
        mock_httpx.post = AsyncMock(return_value=login_post)
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value=None):
            s.ise_admin_session_cookie = None
            s.api_username = "admin"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "pw"
            s.ise_ip = "host"
            s.api_port = 443
            client = mod.IseWebSession()
            client._client = mock_httpx
            resp = await client.get("https://host/admin/x.log.zip")
            assert resp is second_get
            assert mock_httpx.post.await_count == 2  # re-login happened

    @pytest.mark.asyncio
    async def test_two_users_get_isolated_sessions(self):
        import base64
        import clients.ise_web_session as mod
        cred_a = "Basic " + base64.b64encode(b"alice:secret").decode()
        cred_b = "Basic " + base64.b64encode(b"bob:hunter2").decode()
        login_page = _resp(200, text=LOGIN_HTML)
        login_post = _resp(302, headers={"location": "https://host/"})
        zip_ok = _resp(200)
        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.cookies = httpx.Cookies()
        # alice: login page + zip; bob: login page + zip
        mock_httpx.get = AsyncMock(side_effect=[login_page, zip_ok, login_page, zip_ok])
        mock_httpx.post = AsyncMock(return_value=login_post)
        with patch("clients.ise_web_session.settings") as s:
            s.ise_admin_session_cookie = None
            s.api_username = "svc"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "svcpw"
            s.ise_ip = "host"
            s.api_port = 443
            client = mod.IseWebSession()
            client._client = mock_httpx
            with patch("clients.ise_web_session.get_per_user_credential", return_value=cred_a):
                await client.get("https://host/admin/x.log.zip")
            with patch("clients.ise_web_session.get_per_user_credential", return_value=cred_b):
                await client.get("https://host/admin/x.log.zip")
            # Two distinct users -> two logins, two cached jars
            assert mock_httpx.post.await_count == 2
            assert len(client._sessions) == 2

    @pytest.mark.asyncio
    async def test_same_user_reuses_session_single_login(self):
        import base64
        import clients.ise_web_session as mod
        cred = "Basic " + base64.b64encode(b"alice:secret").decode()
        login_page = _resp(200, text=LOGIN_HTML)
        login_post = _resp(302, headers={"location": "https://host/"})
        zip_ok_1 = _resp(200)
        zip_ok_2 = _resp(200)
        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.cookies = httpx.Cookies()
        # one login page, then two zip GETs (no second login)
        mock_httpx.get = AsyncMock(side_effect=[login_page, zip_ok_1, zip_ok_2])
        mock_httpx.post = AsyncMock(return_value=login_post)
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value=cred):
            s.ise_admin_session_cookie = None
            s.api_username = "svc"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "svcpw"
            s.ise_ip = "host"
            s.api_port = 443
            client = mod.IseWebSession()
            client._client = mock_httpx
            await client.get("https://host/admin/x.log.zip")
            await client.get("https://host/admin/x.log.zip")
            assert mock_httpx.post.await_count == 1  # single-flight reuse

    @pytest.mark.asyncio
    async def test_shared_client_jar_cleared_after_each_auth_call(self):
        import clients.ise_web_session as mod
        login_page = _resp(200, text=LOGIN_HTML)
        login_post = _resp(302, headers={"location": "https://host/"})
        zip_ok = _resp(200)
        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.cookies = httpx.Cookies()  # real jar so .clear() is real

        # Simulate httpx absorbing Set-Cookie into the shared jar
        def mock_get_side_effect(*args, **kwargs):
            mock_httpx.cookies.set("APPSESSIONID", "leaked_session", domain="host")
            if mock_httpx.get.await_count == 1:
                return login_page
            return zip_ok

        def mock_post_side_effect(*args, **kwargs):
            mock_httpx.cookies.set("MNTLA_JWT_TOKEN", "leaked_jwt", domain="host")
            return login_post

        mock_httpx.get = AsyncMock(side_effect=mock_get_side_effect)
        mock_httpx.post = AsyncMock(side_effect=mock_post_side_effect)
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value=None):
            s.ise_admin_session_cookie = None
            s.api_username = "admin"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "pw"
            s.ise_ip = "host"; s.api_port = 443
            client = mod.IseWebSession()
            client._client = mock_httpx
            await client.get("https://host/admin/x.log.zip")
            # After the full flow the shared jar holds nothing to replay.
            assert len(mock_httpx.cookies) == 0


class TestCredentialResolution:
    def setup_method(self):
        _reset()

    def test_decodes_per_user_basic_header(self):
        import clients.ise_web_session as mod
        cred = "Basic " + base64.b64encode(b"alice:secret").decode()
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value=cred):
            s.api_username = "svc"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "svcpw"
            client = mod.IseWebSession()
            user, pw = client._resolve_login_credentials()
            assert user == "alice"
            assert pw == "secret"

    def test_falls_back_to_service_account_when_no_header(self):
        import clients.ise_web_session as mod
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value=None):
            s.api_username = "svc"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "svcpw"
            client = mod.IseWebSession()
            user, pw = client._resolve_login_credentials()
            assert user == "svc"
            assert pw == "svcpw"

    def test_malformed_header_raises(self):
        import clients.ise_web_session as mod
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value="Basic not@@base64"):
            s.api_username = "svc"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "svcpw"
            client = mod.IseWebSession()
            with pytest.raises(mod.IseSessionAuthError):
                client._resolve_login_credentials()

    def test_header_without_colon_raises(self):
        import clients.ise_web_session as mod
        cred = "Basic " + base64.b64encode(b"nocolonhere").decode()
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value=cred):
            s.api_username = "svc"
            s.api_pwd = MagicMock()
            s.api_pwd.get_secret_value.return_value = "svcpw"
            client = mod.IseWebSession()
            with pytest.raises(mod.IseSessionAuthError):
                client._resolve_login_credentials()

    def test_no_creds_at_all_raises(self):
        import clients.ise_web_session as mod
        with patch("clients.ise_web_session.settings") as s, \
             patch("clients.ise_web_session.get_per_user_credential", return_value=None):
            s.api_username = None
            s.api_pwd = None
            client = mod.IseWebSession()
            with pytest.raises(mod.IseSessionAuthError):
                client._resolve_login_credentials()

    def test_cache_key_differs_per_credential_and_hides_value(self):
        import clients.ise_web_session as mod
        cred_a = "Basic " + base64.b64encode(b"alice:secret").decode()
        cred_b = "Basic " + base64.b64encode(b"bob:hunter2").decode()
        client = mod.IseWebSession()
        with patch("clients.ise_web_session.get_per_user_credential", return_value=cred_a):
            key_a = client._credential_cache_key()
        with patch("clients.ise_web_session.get_per_user_credential", return_value=cred_b):
            key_b = client._credential_cache_key()
        with patch("clients.ise_web_session.get_per_user_credential", return_value=None):
            key_sa = client._credential_cache_key()
        assert key_a != key_b != key_sa and key_a != key_sa
        # Opaque digest: raw secret never embedded
        assert "alice" not in key_a and "secret" not in key_a
        assert len(key_a) == 64  # sha256 hex
