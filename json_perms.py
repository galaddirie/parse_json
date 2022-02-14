from __future__ import print_function
from typing import Dict, List, TextIO

import json
import csv

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
SERVICE_ACCOUNT_FILE = 'creds.json'
SPREADSHEET_ID = "164HVPQaRCgK-Ht88hrAYtK3GPeLRm1whZBvH7Ujmt1g"


def upload_spreadsheet(table: List[List]) -> None:
    """
    Updates a Google Spreadsheet with a given table of data
    """
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    try:
        service = build('sheets', 'v4', credentials=credentials)

        sheet = service.spreadsheets()
        result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                                        range="sheet1!A1", valueInputOption="USER_ENTERED", body={"values": table}).execute()
    except HttpError as err:
        print(err)


def load_json(file: str) -> Dict:
    """
    pre-condition: file is a json
    """
    with open(file, 'r') as json_file:
        json = json.load(json_file)
    return json


def permissions_to_csv(data: Dict) -> None:
    permissions = []  # gather unique permissions as they appear
    for entry in data:
        for perm in data[entry]:
            if perm not in permissions:
                permissions.append(perm)

    table = [['names'] + permissions]
    for entry in data:
        row = [entry]
        for permission in permissions:
            if permission in data[entry]:
                row.append(1)
            else:
                row.append(0)
        table.append(row)

    with open('result.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        for r in table:
            csv_writer.writerow(r)

    return table


if __name__ == "__main__":
    data = {
        "student1": [
            "view_grades",
            "view_classes"
        ],
        "student2": [
            "view_grades",
            "view_classes"
        ],
        "teacher": [
            "view_grades",
            "change_grades",
            "add_grades",
            "delete_grades",
            "view_classes"
        ],
        "principle": [
            "view_grades",
            "view_classes",
            "change_classes",
            "add_classes",
            "delete_classes"
        ]
    }

    table = permissions_to_csv(data)
    upload_spreadsheet(table)
