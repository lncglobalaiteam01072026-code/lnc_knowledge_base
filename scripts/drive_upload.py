#!/usr/bin/env python3
"""Upload KB files to Google Drive after crawl.

Requires env vars (OAuth2 — set once via scripts/gdrive_setup.py):
  GDRIVE_CLIENT_ID      — OAuth2 desktop app client ID
  GDRIVE_CLIENT_SECRET  — OAuth2 desktop app client secret
  GDRIVE_REFRESH_TOKEN  — long-lived refresh token for vulncglobal@gmail.com
  GDRIVE_FOLDER_ID      — target Drive folder ID (optional, uses default)
"""

import json
import os
import sys
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "1abMW4Bek-eeJlahUOsvZKJCGG9OAsSdQ")
KB_ROOT = Path("output/lnc-knowledge-base")

MIME_MAP = {
    ".md": "text/markdown",
    ".json": "application/json",
    ".csv": "text/csv",
    ".pdf": "application/pdf",
}

_folder_cache: dict[str, str] = {}


def get_service():
    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN")
    client_id = os.environ.get("GDRIVE_CLIENT_ID")
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET")

    if not (refresh_token and client_id and client_secret):
        return None

    from google.oauth2.credentials import Credentials
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def get_or_create_folder(svc, name: str, parent_id: str) -> str:
    key = f"{parent_id}/{name}"
    if key in _folder_cache:
        return _folder_cache[key]

    q = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
        f" and '{parent_id}' in parents and trashed=false"
    )
    res = svc.files().list(q=q, fields="files(id)", pageSize=1).execute()
    files = res.get("files", [])
    if files:
        fid = files[0]["id"]
    else:
        meta = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        fid = svc.files().create(body=meta, fields="id").execute()["id"]

    _folder_cache[key] = fid
    return fid


def upload_file(svc, path: Path, parent_id: str):
    name = path.name
    mime = MIME_MAP.get(path.suffix, "application/octet-stream")

    q = f"name='{name}' and '{parent_id}' in parents and trashed=false"
    res = svc.files().list(q=q, fields="files(id)", pageSize=1).execute()
    existing = res.get("files", [])

    media = MediaFileUpload(str(path), mimetype=mime, resumable=path.stat().st_size > 5_000_000)

    rel = path.relative_to(KB_ROOT)
    if existing:
        svc.files().update(fileId=existing[0]["id"], media_body=media).execute()
        print(f"  updated  {rel}")
    else:
        meta = {"name": name, "parents": [parent_id]}
        svc.files().create(body=meta, media_body=media, fields="id").execute()
        print(f"  created  {rel}")


def upload_dir(svc, local: Path, drive_parent: str):
    for item in sorted(local.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir():
            fid = get_or_create_folder(svc, item.name, drive_parent)
            upload_dir(svc, item, fid)
        elif item.is_file() and item.suffix in MIME_MAP:
            upload_file(svc, item, drive_parent)


def main():
    if not KB_ROOT.exists():
        print("KB root not found — skipping Drive upload")
        sys.exit(0)

    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN")
    client_id = os.environ.get("GDRIVE_CLIENT_ID")
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET")

    if not (refresh_token and client_id and client_secret):
        print("GDRIVE_REFRESH_TOKEN / GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET not set")
        print("Run scripts/gdrive_setup.py once to configure OAuth2 credentials.")
        sys.exit(0)

    print(f"Uploading KB → Drive folder {FOLDER_ID}")
    svc = get_service()
    try:
        upload_dir(svc, KB_ROOT, FOLDER_ID)
        print("Drive upload complete.")
    except HttpError as e:
        print(f"Drive upload failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
