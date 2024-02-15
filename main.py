import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel

class InsertEntryBody(BaseModel):
    user: str
    type: str
    category: str
    timestamp: str
    amount: float

class DeleteEntryBody(BaseModel):
    user: str
    index: str

def initializeSpreadsheetAPI(spreadsheetLink):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = './spreadsheetKeys.json'
    credentials = None
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    SAMPLE_SPREADSHEET_ID = spreadsheetLink
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    return sheet, SAMPLE_SPREADSHEET_ID

sheetFederico, SAMPLE_SPREADSHEET_ID_FEDERICO = "", ""
sheetCarolina, SAMPLE_SPREADSHEET_ID_CAROLINA = "", ""

try:
    f = open("./spreadsheetLinks.json")
    data = json.load(f)
    sheetFederico, SAMPLE_SPREADSHEET_ID_FEDERICO = initializeSpreadsheetAPI(data["life_balance_federico"])
    sheetCarolina, SAMPLE_SPREADSHEET_ID_CAROLINA = initializeSpreadsheetAPI(data["life_balance_carolina"])
    
except IndexError as e:
    print(e)

app = FastAPI()



@app.post("/insert_entry/")
async def create_item(item: InsertEntryBody):
    if (item.user == "Federico"):
        sheet, SAMPLE_SPREADSHEET_ID = sheetFederico, SAMPLE_SPREADSHEET_ID_FEDERICO
    else:
        sheet, SAMPLE_SPREADSHEET_ID = sheetCarolina, SAMPLE_SPREADSHEET_ID_CAROLINA
    
    try:
    #updating the value
        sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
            range= "DB!A1" , valueInputOption="USER_ENTERED", body={"values":[[item.type, item.category, item.timestamp, item.amount]]}).execute()
    except e:
        return Exception(e)
    return '200'

@app.post("/delete_entry/")
async def create_item(item: DeleteEntryBody):
    if (item.user == "Federico"):
        sheet, SAMPLE_SPREADSHEET_ID, offset = sheetFederico, SAMPLE_SPREADSHEET_ID_FEDERICO, 270
    else:
        sheet, SAMPLE_SPREADSHEET_ID, offset = sheetCarolina, SAMPLE_SPREADSHEET_ID_CAROLINA, 42

    #deleting index row
    request_body = {
        'requests': [ 
            {
                'deleteDimension': {
                    'range': {
                        'sheetId' : '999176741',
                        'dimension': 'ROWS',
                        'startIndex': int(item.index) + offset - 1,
                        'endIndex': int(item.index) + offset
                    }

                }
            }       
        ]
    }

    try:
        sheet.batchUpdate(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            body=request_body
        ).execute()
    except e:
        return Exception(e)
    return '200'