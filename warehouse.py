from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import io
import os

# ==========================
# AUTHENTICATION
# ==========================

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=SCOPES
)

service = build('drive', 'v3', credentials=creds)

# ==========================
# DRIVE FOLDER IDS
# ==========================

INCREFF_FOLDER = "1OJwqqwkTqwITho8XaMitO39E509iV10S"
OUTPUT_FOLDER = "1nTAlKWVEv6WozRb_Lcim75QTTKxuwKh2"

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ==========================
# DOWNLOAD REPORTS
# ==========================

results = service.files().list(
    q=f"'{INCREFF_FOLDER}' in parents",
    fields="files(id, name)"
).execute()

files = results.get('files', [])

dataframes = []

for file in files:
    request = service.files().get_media(fileId=file['id'])
    fh = io.FileIO(f"{DOWNLOAD_PATH}/{file['name']}", 'wb')

    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    print("Downloaded:", file['name'])

    df = pd.read_excel(f"{DOWNLOAD_PATH}/{file['name']}")
    dataframes.append(df)

# ==========================
# WAREHOUSE CALCULATION
# ==========================

combined = pd.concat(dataframes, ignore_index=True)

# Example calculation
combined["Available Stock"] = (
    combined["Inward Qty"] -
    combined["Dispatch Qty"]
)

combined["Shortage"] = (
    combined["System Stock"] -
    combined["Physical Stock"]
)

# ==========================
# SAVE OUTPUT
# ==========================

output_file = "Warehouse_Output.xlsx"
combined.to_excel(output_file, index=False)

print("Warehouse calculation completed")
