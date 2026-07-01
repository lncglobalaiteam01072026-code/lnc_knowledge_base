#!/usr/bin/env python3
"""Build /tmp/rclone.conf from GDRIVE_REFRESH_TOKEN and run Drive sync.

rclone v1.74+ skips the refresh_token pre-check only when access_token is
non-empty, so we use a dummy value here to trigger the OAuth refresh path
rather than the "no refresh token" early-exit path.
"""
import json
import os
import subprocess
import sys

rt = os.environ["GDRIVE_REFRESH_TOKEN"].strip()
if not rt:
    raise SystemExit("GDRIVE_REFRESH_TOKEN is empty")

token = json.dumps({
    "access_token": "dummy_expired_token",
    "token_type": "Bearer",
    "refresh_token": rt,
    "expiry": "2020-01-01T00:00:00.000000000Z",
}, separators=(",", ":"))

client_id = os.environ.get("GDRIVE_CLIENT_ID", "")
client_secret = os.environ.get("GDRIVE_CLIENT_SECRET", "")

conf = "[gdrive]\ntype = drive\nscope = drive\n"
if client_id:
    conf += f"client_id = {client_id}\n"
if client_secret:
    conf += f"client_secret = {client_secret}\n"
conf += "token = " + token + "\n"
with open("/tmp/rclone.conf", "w") as f:
    f.write(conf)
print("rclone.conf written")

# Run the sync here so the workflow shell command is a no-op.
# This avoids issues with debug flags like --log-level DEBUG | head -N
# that can truncate output and kill the sync prematurely.
kb_dir = os.path.join(os.getcwd(), "output", "lnc-knowledge-base")
if os.path.isdir(kb_dir):
    print("Starting Drive sync...")
    result = subprocess.run(
        [
            "rclone", "--config", "/tmp/rclone.conf",
            "sync", kb_dir, "gdrive:lnc-knowledge-base-temp",
            "--exclude", ".git/**",
            "--transfers", "8",
            "--fast-list",
        ],
        check=False,
    )
    if result.returncode != 0:
        print(f"rclone sync exited with code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)
    print("Drive sync complete")
else:
    print(f"KB directory not found at {kb_dir}, skipping sync", file=sys.stderr)
