from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import io
import os

# ==============================
# GOOGLE DRIVE AUTH
# ==============================

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=SCOPES
)

service = build('drive', 'v3', credentials=creds)

# ==============================
# FOLDER ID (CHANGE THIS)
# ==============================

FOLDER_ID = "1OJwqqwkTqwITho8XaMitO39E509iV10S"

DOWNLOAD_PATH = "downloads"

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ==============================
# LIST FILES
# ==============================

results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    fields="files(id, name)"
).execute()

files = results.get('files', [])

print("Files Found:", len(files))

# ==============================
# DOWNLOAD FILES
# ==============================

for file in files:
    request = service.files().get_media(fileId=file['id'])
    fh = io.FileIO(f"{DOWNLOAD_PATH}/{file['name']}", 'wb')

    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    print(f"Downloaded: {file['name']}")

print("Drive sync completed")
