from __future__ import annotations

import base64
import json
import secrets
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from linkedin_connector.config import SETTINGS


AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
AUTH_STORE_PATH = Path.home() / ".linkedin_jobs_connector_auth.json"


class LinkedInAuthService:
    def get_status(self) -> dict[str, Any]:
        config_ready = bool(SETTINGS.linkedin_client_id and SETTINGS.linkedin_client_secret and SETTINGS.linkedin_redirect_uri)
        token_data = self._read_store()
        token_present = bool(token_data.get("access_token"))
        return {
            "configured": config_ready,
            "authenticated": token_present,
            "redirect_uri": SETTINGS.linkedin_redirect_uri,
            "scopes": SETTINGS.linkedin_scopes.split(),
            "profile": token_data.get("profile", {}),
            "auth_store_path": str(AUTH_STORE_PATH),
            "limitations": [
                "Official LinkedIn sign-in can authenticate the member.",
                "Open permissions do not grant broad access to jobs or 2nd/3rd degree connection data.",
                "Additional LinkedIn partner approvals are required for restricted APIs.",
            ],
        }

    def begin_login(self) -> dict[str, Any]:
        self._ensure_configured()
        state = secrets.token_urlsafe(24)
        verifier = secrets.token_urlsafe(32)
        store_data = self._read_store()
        store_data["pending_state"] = state
        store_data["pending_verifier"] = verifier
        store_data["updated_at"] = int(time.time())
        self._write_store(store_data)

        params = {
            "response_type": "code",
            "client_id": SETTINGS.linkedin_client_id,
            "redirect_uri": SETTINGS.linkedin_redirect_uri,
            "state": state,
            "scope": SETTINGS.linkedin_scopes,
        }
        auth_url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
        return {
            "auth_url": auth_url,
            "redirect_uri": SETTINGS.linkedin_redirect_uri,
            "next_step": "Open auth_url in the browser, sign in to LinkedIn, approve access, then pass the full redirected URL into linkedin_complete_login.",
        }

    def complete_login(self, redirected_url: str) -> dict[str, Any]:
        self._ensure_configured()
        parsed = urllib.parse.urlparse(redirected_url)
        query = urllib.parse.parse_qs(parsed.query)
        code = self._require_single(query, "code")
        state = self._require_single(query, "state")

        store_data = self._read_store()
        expected_state = store_data.get("pending_state")
        if not expected_state or expected_state != state:
            raise ValueError("state mismatch; run linkedin_begin_login again before completing login")

        payload = urllib.parse.urlencode(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": SETTINGS.linkedin_redirect_uri,
                "client_id": SETTINGS.linkedin_client_id,
                "client_secret": SETTINGS.linkedin_client_secret,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            TOKEN_URL,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=SETTINGS.provider_timeout_seconds) as response:
            token_data = json.loads(response.read().decode("utf-8"))

        profile = self._decode_id_token_profile(token_data.get("id_token", ""))
        updated_store = {
            "access_token": token_data.get("access_token", ""),
            "expires_in": token_data.get("expires_in", 0),
            "id_token": token_data.get("id_token", ""),
            "scope": token_data.get("scope", SETTINGS.linkedin_scopes),
            "profile": profile,
            "authenticated_at": int(time.time()),
            "updated_at": int(time.time()),
        }
        self._write_store(updated_store)

        return {
            "authenticated": True,
            "profile": profile,
            "expires_in": token_data.get("expires_in", 0),
            "scope": token_data.get("scope", SETTINGS.linkedin_scopes),
        }

    def logout(self) -> dict[str, Any]:
        if AUTH_STORE_PATH.exists():
            AUTH_STORE_PATH.unlink()
        return {"authenticated": False, "auth_store_path": str(AUTH_STORE_PATH)}

    def _ensure_configured(self) -> None:
        missing = []
        if not SETTINGS.linkedin_client_id:
            missing.append("LINKEDIN_CLIENT_ID")
        if not SETTINGS.linkedin_client_secret:
            missing.append("LINKEDIN_CLIENT_SECRET")
        if not SETTINGS.linkedin_redirect_uri:
            missing.append("LINKEDIN_REDIRECT_URI")
        if missing:
            raise ValueError(f"missing required LinkedIn OAuth config: {', '.join(missing)}")

    @staticmethod
    def _require_single(query: dict[str, list[str]], key: str) -> str:
        values = query.get(key, [])
        if not values or not values[0]:
            raise ValueError(f"redirected URL is missing '{key}'")
        return values[0]

    @staticmethod
    def _read_store() -> dict[str, Any]:
        if not AUTH_STORE_PATH.exists():
            return {}
        return json.loads(AUTH_STORE_PATH.read_text())

    @staticmethod
    def _write_store(data: dict[str, Any]) -> None:
        AUTH_STORE_PATH.write_text(json.dumps(data, indent=2))

    @staticmethod
    def _decode_id_token_profile(id_token: str) -> dict[str, Any]:
        if not id_token or "." not in id_token:
            return {}
        try:
            payload_b64 = id_token.split(".")[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            decoded = base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8")
            return json.loads(decoded)
        except Exception:
            return {}
