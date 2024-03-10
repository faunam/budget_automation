# methodology from this video https://www.youtube.com/watch?v=tamT_iGoZDQ&ab_channel=ShanmugamUdhaya
# must set up google cloud service and enable google drive API on it, see instructions on setup: https://developers.google.com/workspace/guides/create-credentials#service-account

from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

load_dotenv()
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = os.getenv("DRIVE_PARENT_FOLDER_ID")
PROCESSED_FOLDER_ID = os.getenv("DRIVE_PROCESSED_FOLDER_ID")

def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def upload(service, filepath):
    file_metadata = {
        'name': filepath,
        'parents': [PARENT_FOLDER_ID]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=filepath
    ).execute()

def clear_processed_files(service):
    files_obj = service.files().list(
        q=f"'{PROCESSED_FOLDER_ID}' in parents",
        fields="files(id, name)"
    ).execute()

    files = files_obj['files']

    for file in files:
        service.files().delete(
            fileId=file['id'],
        ).execute()

def main():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    upload(service, 'transactions_test.csv')
    clear_processed_files(service)

main()

