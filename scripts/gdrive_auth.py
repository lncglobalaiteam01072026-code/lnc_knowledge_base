#!/usr/bin/env python3
"""Run once locally to get Google Drive OAuth refresh token.

Usage:
  pip install google-auth-oauthlib
  python scripts/gdrive_auth.py

Then set 3 GitHub secrets:
  GDRIVE_CLIENT_ID
  GDRIVE_CLIENT_SECRET
  GDRIVE_REFRESH_TOKEN
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

client_id = input("Client ID: ").strip()
client_secret = input("Client Secret: ").strip()

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    SCOPES,
)

creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

print("\n" + "=" * 60)
print("Set these 3 secrets in GitHub repo → Settings → Secrets:")
print(f"  GDRIVE_CLIENT_ID     = {client_id}")
print(f"  GDRIVE_CLIENT_SECRET = {client_secret}")
print(f"  GDRIVE_REFRESH_TOKEN = {creds.refresh_token}")
print("=" * 60)
