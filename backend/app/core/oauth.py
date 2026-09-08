"""
Minimal OAuth2 authorization-code flow for Google and Microsoft login.

No extra dependency (Authlib etc) - this is standard OAuth2 and httpx
handles it fine. Each provider needs three things from you in .env:
CLIENT_ID, CLIENT_SECRET, and a REDIRECT_URI that's registered exactly in
that provider's developer console.

Flow (same shape for both providers):
  1. GET /api/auth/{provider}/login  -> 302 redirect to provider's consent screen
  2. User approves -> provider redirects back to our callback with ?code=...
  3. GET /api/auth/{provider}/callback -> exchange code for an access token,
     fetch the user's email/name, find-or-create a User row, issue OUR OWN
     JWT (same one email/password login issues), redirect to the frontend
     with that token in the URL so the SPA can pick it up.
"""
import httpx
from urllib.parse import urlencode

from app.core.config import get_settings

settings = get_settings()


class OAuthError(Exception):
    pass


# ---------------------------------------------------------------- Google --

def google_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "state": state,
        "prompt": "select_account",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


async def google_fetch_user(code: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            },
        )
        if token_resp.status_code != 200:
            raise OAuthError(f"Google token exchange failed: {token_resp.text}")
        access_token = token_resp.json()["access_token"]

        userinfo_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_resp.status_code != 200:
            raise OAuthError(f"Google userinfo fetch failed: {userinfo_resp.text}")
        info = userinfo_resp.json()

        return {"email": info["email"], "name": info.get("name")}


# ------------------------------------------------------------- Microsoft --

def microsoft_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "response_type": "code",
        "response_mode": "query",
        "scope": "openid email profile User.Read",
        "state": state,
    }
    base = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT}/oauth2/v2.0/authorize"
    return f"{base}?{urlencode(params)}"


async def microsoft_fetch_user(code: str) -> dict:
    token_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT}/oauth2/v2.0/token"
    async with httpx.AsyncClient(timeout=10) as client:
        token_resp = await client.post(
            token_url,
            data={
                "client_id": settings.MICROSOFT_CLIENT_ID,
                "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
                "scope": "openid email profile User.Read",
            },
        )
        if token_resp.status_code != 200:
            raise OAuthError(f"Microsoft token exchange failed: {token_resp.text}")
        access_token = token_resp.json()["access_token"]

        userinfo_resp = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_resp.status_code != 200:
            raise OAuthError(f"Microsoft Graph /me fetch failed: {userinfo_resp.text}")
        info = userinfo_resp.json()

        # Personal Microsoft accounts put email in "mail"; work/school
        # accounts sometimes only populate "userPrincipalName".
        email = info.get("mail") or info.get("userPrincipalName")
        if not email:
            raise OAuthError("Microsoft account has no usable email address")

        return {"email": email, "name": info.get("displayName")}
