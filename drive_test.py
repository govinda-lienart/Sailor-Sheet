# drive_upload.py
# Purpose: Upload a uniquely named file into a Shared Drive folder (Bills WebApp) via Service Account.
# Actions:
#   1) Check folder access
#   2) Upload either (A) a small in-memory text file, OR (B) a real local file if LOCAL_FILE_PATH is set
#   3) List files in the folder
#
# Requirements:
#   pip install google-api-python-client google-auth google-auth-httplib2 python-dotenv
#   .env must contain GOOGLE_CREDENTIALS=<your service account JSON>
#
# Notes:
#   - Make sure the Service Account is a MEMBER of the Shared drive (Content manager or Manager).
#   - Use the folder ID from the Shared Drive (not My Drive).
#   - This script KEEPS the uploaded file (no deletion).

import os
import json
import io
from datetime import datetime
from dotenv import load_dotenv

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload

print("🚀 Starting Google Drive Shared-Drive upload test...")

# ----------------------------
# 1) Configuration
# ----------------------------
load_dotenv()

# Shared Drive folder ID (Bills WebApp) — from your link:
FOLDER_ID = "1UH-mqbvJ6k6Y0wDD4x7DcDRzsEjf0Rz0"

# If you want to upload a real local file (e.g., a PDF), put its path here (or leave as None)
# Example: LOCAL_FILE_PATH = "/Users/you/Downloads/invoice.pdf"
LOCAL_FILE_PATH = None  # <-- change this if you want to upload a real file

# Scopes — Drive is enough for this test
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Content used if we upload the in-memory test text file
TEST_CONTENT = "Hello from the NGO Accounting App (Shared drive test)."

def unique_name(base: str, ext: str) -> str:
    """Generate a unique filename with timestamp, e.g., base_2025-08-30_14-22-05.ext"""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{base}_{ts}.{ext}"

# ----------------------------
# 2) Auth (Service Account from .env)
# ----------------------------
def get_service_account_credentials():
    gc_env = os.getenv("GOOGLE_CREDENTIALS")
    if not gc_env:
        raise RuntimeError(
            "GOOGLE_CREDENTIALS missing in .env. "
            "Paste your Service Account JSON into GOOGLE_CREDENTIALS."
        )
    info = json.loads(gc_env)
    return Credentials.from_service_account_info(info, scopes=SCOPES)

def build_drive_service(creds):
    return build("drive", "v3", credentials=creds)

# ----------------------------
# 3) Drive helpers (Shared Drives)
# ----------------------------
def check_folder_access(drive):
    print("🔍 Checking access to folder...")
    folder = drive.files().get(
        fileId=FOLDER_ID,
        supportsAllDrives=True,
        fields="id,name,parents"
    ).execute()
    print(f"✅ Folder OK: {folder['name']} ({folder['id']})")

def upload_text_file(drive):
    """Upload the small test text file (in memory) with a unique name."""
    print("⬆️ Uploading in-memory test text file to Shared Drive folder...")
    filename = unique_name("test_upload_shared_drive", "txt")
    media = MediaIoBaseUpload(
        io.BytesIO(TEST_CONTENT.encode("utf-8")),
        mimetype="text/plain",
        resumable=True
    )
    file = drive.files().create(
        body={"name": filename, "parents": [FOLDER_ID]},
        media_body=media,
        fields="id,name,webViewLink",
        supportsAllDrives=True
    ).execute()
    print(f"✅ Uploaded: {file['name']} ({file['id']})")
    print(f"   Open in Drive: {file['webViewLink']}")
    return file["id"], file["name"]

def upload_local_file(drive, path: str):
    """Upload a real local file with a unique name (base name + timestamp)."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Local file not found: {path}")

    base = os.path.splitext(os.path.basename(path))[0]
    ext = os.path.splitext(path)[1].lstrip(".") or "bin"
    filename = unique_name(base, ext)

    print(f"⬆️ Uploading local file to Shared Drive folder: {path} -> {filename}")
    media = MediaFileUpload(path, resumable=True)
    file = drive.files().create(
        body={"name": filename, "parents": [FOLDER_ID]},
        media_body=media,
        fields="id,name,webViewLink",
        supportsAllDrives=True
    ).execute()
    print(f"✅ Uploaded: {file['name']} ({file['id']})")
    print(f"   Open in Drive: {file['webViewLink']}")
    return file["id"], file["name"]

def list_folder_files(drive):
    print("📂 Listing files in the folder...")
    res = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        fields="files(id,name,webViewLink)",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        corpora="allDrives"
    ).execute()
    files = res.get("files", [])
    print(f"✅ Found {len(files)} file(s):")
    for f in files:
        print(f"   - {f['name']} ({f['id']})")
    return files

# ----------------------------
# 4) Main
# ----------------------------
if __name__ == "__main__":
    creds = get_service_account_credentials()
    drive = build_drive_service(creds)

    check_folder_access(drive)

    if LOCAL_FILE_PATH:
        upload_local_file(drive, LOCAL_FILE_PATH)
    else:
        upload_text_file(drive)

    list_folder_files(drive)
    print("🎉 Shared-drive upload test completed (file kept).")