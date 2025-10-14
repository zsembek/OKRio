"""Azure Active Directory OAuth 2.0 client helpers."""
from __future__ import annotations

import base64
import hashlib
import os
from typing import Iterable
from urllib.parse import urlencode

import httpx

from ....core.config import Settings
from ..schemas import AzureOAuthTokenResponse


class AzureOAuthClient:
    """Lightweight wrapper that builds OAuth 2.0 requests for Azure AD."""

    authorize_path = "/oauth2/v2.0/authorize"
    token_path = "/oauth2/v2.0/token"
    logout_path = "/oauth2/v2.0/logout"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    # -- Authorization helpers ---------------------------------------------
    def build_authorization_url(
        self,
        state: str,
        nonce: str | None = None,
        scopes: Iterable[str] | None = None,
        redirect_uri: str | None = None,
        code_verifier: str | None = None,
        code_challenge: str | None = None,
        code_challenge_method: str = "S256",
    ) -> tuple[str, str | None]:
        """Return the authorization URL and optional PKCE verifier."""

        effective_scopes = " ".join(scopes or self.settings.azure_oauth_scopes.split())
        redirect = redirect_uri or str(self.settings.azure_redirect_uri_frontend)
        query = {
            "client_id": self.settings.azure_client_id,
            "response_type": "code",
            "redirect_uri": redirect,
            "response_mode": "query",
            "scope": effective_scopes,
            "state": state,
        }
        if nonce:
            query["nonce"] = nonce
        verifier = code_verifier
        if code_challenge is None:
            verifier = verifier or generate_pkce_verifier()
            code_challenge = build_pkce_challenge(verifier)
        if code_challenge:
            query["code_challenge"] = code_challenge
            query["code_challenge_method"] = code_challenge_method

        return (
            f"{self.settings.azure_authority}{self.authorize_path}?{urlencode(query)}",
            verifier,
        )

    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: str | None = None,
    ) -> AzureOAuthTokenResponse:
        """Exchange an authorization code for Azure AD tokens."""

        data = {
            "client_id": self.settings.azure_client_id,
            "scope": self.settings.azure_oauth_scopes,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        if code_verifier:
            data["code_verifier"] = code_verifier
        if self.settings.azure_client_secret:
            data["client_secret"] = self.settings.azure_client_secret

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.settings.azure_authority}{self.token_path}",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=20.0,
            )
            response.raise_for_status()
            payload = response.json()
        return AzureOAuthTokenResponse.parse_obj(payload)

    async def refresh_access_token(self, refresh_token: str) -> AzureOAuthTokenResponse:
        """Refresh an Azure AD access token."""

        data = {
            "client_id": self.settings.azure_client_id,
            "scope": self.settings.azure_oauth_scopes,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        if self.settings.azure_client_secret:
            data["client_secret"] = self.settings.azure_client_secret

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.settings.azure_authority}{self.token_path}",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=20.0,
            )
            response.raise_for_status()
            payload = response.json()
        return AzureOAuthTokenResponse.parse_obj(payload)

    def build_logout_url(self, post_logout_redirect_uri: str | None = None) -> str:
        """Construct the Azure logout endpoint for front-channel sign-out."""

        redirect = post_logout_redirect_uri or str(self.settings.azure_logout_redirect_uri)
        query = {"post_logout_redirect_uri": redirect, "client_id": self.settings.azure_client_id}
        return f"{self.settings.azure_authority}{self.logout_path}?{urlencode(query)}"


def generate_pkce_verifier(length: int = 64) -> str:
    """Create a high-entropy code verifier for PKCE flows."""

    return base64.urlsafe_b64encode(os.urandom(length)).decode("utf-8").rstrip("=")


def build_pkce_challenge(code_verifier: str) -> str:
    """Derive the S256 challenge from the code verifier."""

    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
