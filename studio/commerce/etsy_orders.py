#!/usr/bin/env python3
"""Connect to the Etsy Open API v3 and pull new orders + their personalization.

This is the read side of the automation loop: it authenticates your Etsy shop
via OAuth 2.0 (Authorization Code + PKCE), then polls `getShopReceipts` for new
paid orders and prints each buyer's personalization answers (address, radius,
theme, child's name, etc.) so you can feed them into the map generator.

It does NOT push anything back to Etsy or Prodigi — it's the "read new orders"
building block. Fulfilment/tracking can be added later once the render pipeline
is automated.

--- Setup (one time) --------------------------------------------------------
  1. Create an app: https://www.etsy.com/developers/your-apps  (approval ~1-2 days)
  2. Register a redirect URI on the app EXACTLY as:  http://localhost:3003/callback
  3. Put your credentials in a .env file at the repo root (gitignored):
        ETSY_API_KEY=your-keystring
        # ETSY_SHOP_ID is optional; auto-discovered from your token if omitted.
  4. Authorize (opens a browser, saves tokens to .etsy_tokens.json):
        uv run python studio/commerce/etsy_orders.py auth
  5. List recent orders + personalization:
        uv run python studio/commerce/etsy_orders.py orders --days 30

Docs: https://developers.etsy.com/documentation/essentials/authentication/
Note: Etsy data is Etsy's; OSM playground data stays ODbL-attributed downstream.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import sys
import time
import urllib.parse
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOKEN_FILE = REPO_ROOT / ".etsy_tokens.json"

OAUTH_CONNECT = "https://www.etsy.com/oauth/connect"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
API_BASE = "https://openapi.etsy.com/v3/application"

# transactions_r = read purchases/sales (receipts). email_r = buyer email field.
SCOPES = "transactions_r email_r"

REDIRECT_HOST = "localhost"
REDIRECT_PORT = 3003
REDIRECT_URI = f"http://{REDIRECT_HOST}:{REDIRECT_PORT}/callback"


# --------------------------------------------------------------------------- #
# env + token persistence
# --------------------------------------------------------------------------- #
def load_dotenv(path: Path) -> None:
    """Minimal .env loader so we don't add a dependency."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def save_tokens(data: dict) -> None:
    data = {**data, "obtained_at": int(time.time())}
    TOKEN_FILE.write_text(json.dumps(data, indent=2))
    TOKEN_FILE.chmod(0o600)


def load_tokens() -> dict | None:
    if not TOKEN_FILE.exists():
        return None
    return json.loads(TOKEN_FILE.read_text())


# --------------------------------------------------------------------------- #
# PKCE
# --------------------------------------------------------------------------- #
def make_pkce() -> tuple[str, str]:
    """Return (code_verifier, code_challenge) per RFC 7636 / Etsy requirements."""
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b"=").decode()
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


class _CallbackHandler(BaseHTTPRequestHandler):
    """One-shot handler that captures ?code=&state= from Etsy's redirect."""

    result: dict = {}

    def do_GET(self):  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return
        _CallbackHandler.result = dict(urllib.parse.parse_qsl(parsed.query))
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<html><body style='font-family:sans-serif'>"
            b"<h2>Etsy connected.</h2><p>You can close this tab and return to the terminal.</p>"
            b"</body></html>"
        )

    def log_message(self, *args):  # silence the default stderr logging
        pass


# --------------------------------------------------------------------------- #
# OAuth flow
# --------------------------------------------------------------------------- #
def cmd_auth(api_key: str) -> int:
    verifier, challenge = make_pkce()
    state = secrets.token_urlsafe(24)
    params = {
        "response_type": "code",
        "client_id": api_key,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{OAUTH_CONNECT}?{urllib.parse.urlencode(params)}"

    print("Opening browser to authorize the app on Etsy...")
    print(f"  If it doesn't open, paste this URL:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    server = HTTPServer((REDIRECT_HOST, REDIRECT_PORT), _CallbackHandler)
    print(f"Waiting for the redirect on {REDIRECT_URI} ...")
    server.handle_request()  # blocks until Etsy hits the callback once
    resp = _CallbackHandler.result

    if resp.get("error"):
        print(f"ERROR from Etsy: {resp.get('error')} — {resp.get('error_description')}", file=sys.stderr)
        return 1
    if resp.get("state") != state:
        print("ERROR: state mismatch — possible CSRF. Aborting.", file=sys.stderr)
        return 1
    code = resp.get("code")
    if not code:
        print("ERROR: no authorization code returned.", file=sys.stderr)
        return 1

    token_resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": api_key,
            "redirect_uri": REDIRECT_URI,
            "code": code,
            "code_verifier": verifier,
        },
        timeout=30,
    )
    if token_resp.status_code != 200:
        print(f"ERROR exchanging code: HTTP {token_resp.status_code}\n{token_resp.text}", file=sys.stderr)
        return 1

    save_tokens(token_resp.json())
    print(f"Authorized. Tokens saved to {TOKEN_FILE.name} (access token lasts 1h; auto-refreshed).")
    return 0


def refresh_access_token(api_key: str, tokens: dict) -> dict:
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": api_key,
            "refresh_token": tokens["refresh_token"],
        },
        timeout=30,
    )
    resp.raise_for_status()
    new = resp.json()
    save_tokens(new)
    return new


def valid_access_token(api_key: str) -> str:
    tokens = load_tokens()
    if not tokens:
        print("Not authorized yet. Run:  uv run python studio/commerce/etsy_orders.py auth", file=sys.stderr)
        raise SystemExit(1)
    # Refresh a bit early (tokens live 3600s).
    age = int(time.time()) - tokens.get("obtained_at", 0)
    if age > tokens.get("expires_in", 3600) - 120:
        tokens = refresh_access_token(api_key, tokens)
    return tokens["access_token"]


# --------------------------------------------------------------------------- #
# API calls
# --------------------------------------------------------------------------- #
def api_get(api_key: str, token: str, path: str, params: dict | None = None) -> dict:
    resp = requests.get(
        f"{API_BASE}{path}",
        headers={"x-api-key": api_key, "Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def discover_shop_id(api_key: str, token: str) -> str:
    me = api_get(api_key, token, "/users/me")
    shop_id = me.get("shop_id")
    if not shop_id:
        raise SystemExit("Could not determine shop_id from /users/me — set ETSY_SHOP_ID in .env.")
    return str(shop_id)


def cmd_orders(api_key: str, shop_id: str | None, days: int) -> int:
    token = valid_access_token(api_key)
    shop_id = shop_id or discover_shop_id(api_key, token)

    min_created = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    data = api_get(
        api_key,
        token,
        f"/shops/{shop_id}/receipts",
        params={"min_created": min_created, "limit": 100, "was_paid": "true"},
    )
    receipts = data.get("results", [])
    print(f"Shop {shop_id}: {len(receipts)} paid receipt(s) in the last {days} day(s).\n")

    for r in receipts:
        when = datetime.fromtimestamp(r.get("created_timestamp", 0), tz=timezone.utc).strftime("%Y-%m-%d")
        name = r.get("name", "?")
        email = r.get("buyer_email", "(email scope not granted)")
        status = "SHIPPED" if r.get("is_shipped") else "NOT SHIPPED"
        print(f"── Receipt {r.get('receipt_id')}  [{when}]  {name}  <{email}>  {status}")

        for t in r.get("transactions", []):
            title = t.get("title", "(item)")
            qty = t.get("quantity", 1)
            print(f"     • {qty}x {title}")
            for v in t.get("variations", []):
                fname = v.get("formatted_name", v.get("property_id"))
                fval = v.get("formatted_value", "")
                print(f"         - {fname}: {fval}")
            # Personalization on newer listings may arrive as a dedicated field.
            personalization = t.get("personalization") or t.get("buyer_personalization")
            if personalization:
                print(f"         - Personalization: {personalization}")
        print()

    if not receipts:
        print("No orders yet in this window. Try a larger --days value.")
    return 0


# --------------------------------------------------------------------------- #
def main(argv: list[str]) -> int:
    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get("ETSY_API_KEY")
    shop_id = os.environ.get("ETSY_SHOP_ID")

    if not api_key:
        print(
            "ERROR: ETSY_API_KEY not set.\n"
            "  1. Create an app at https://www.etsy.com/developers/your-apps\n"
            "  2. Add to .env:  ETSY_API_KEY=your-keystring\n",
            file=sys.stderr,
        )
        return 1

    cmd = argv[0] if argv else "orders"

    if cmd == "auth":
        return cmd_auth(api_key)

    if cmd == "orders":
        days = 30
        if "--days" in argv:
            days = int(argv[argv.index("--days") + 1])
        return cmd_orders(api_key, shop_id, days)

    print(f"Unknown command {cmd!r}. Use:  auth  |  orders [--days N]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
