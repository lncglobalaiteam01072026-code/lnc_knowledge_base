#!/usr/bin/env python3
"""One-time OAuth2 setup for Google Drive uploads.

Run this script once to obtain a refresh token for the Drive folder owner
(vulncglobal@gmail.com) and store it as GitHub Actions secrets.

Usage:
  python scripts/gdrive_setup.py client_secret.json

To get client_secret.json:
  1. Open: https://console.cloud.google.com/apis/credentials?project=circular-truck-500815-u5
  2. Click "Create Credentials" → "OAuth client ID"
  3. Application type: "Desktop app"  (name it anything)
  4. Click "Create", then "Download JSON"
  5. Save it and pass the path to this script
"""

import json
import subprocess
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive"]


def ensure_deps():
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow  # noqa: F401
    except ImportError:
        print("Installing google-auth-oauthlib...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "google-auth-oauthlib"],
            check=True,
        )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    client_file = Path(sys.argv[1])
    if not client_file.exists():
        print(f"File not found: {client_file}")
        sys.exit(1)

    ensure_deps()
    from google_auth_oauthlib.flow import InstalledAppFlow

    print("Starting OAuth2 flow — a browser window will open.")
    print("Log in as vulncglobal@gmail.com and click Allow.")
    flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    client_info = json.loads(client_file.read_text())
    installed = client_info.get("installed", client_info.get("web", {}))

    credentials = {
        "GDRIVE_CLIENT_ID": installed["client_id"],
        "GDRIVE_CLIENT_SECRET": installed["client_secret"],
        "GDRIVE_REFRESH_TOKEN": creds.refresh_token,
    }

    print("\nOAuth2 credentials obtained. Setting GitHub secrets...")
    for name, value in credentials.items():
        result = subprocess.run(
            ["gh", "secret", "set", name, "--body", value],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  set {name}")
        else:
            print(f"  FAILED {name}: {result.stderr.strip()}")

    print("\nDone. GitHub Actions will now upload KB files to Google Drive.")
    print("You can delete the client_secret.json file (secrets are in GitHub now).")


if __name__ == "__main__":
    main()
