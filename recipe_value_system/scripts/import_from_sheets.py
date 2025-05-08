"""
Import recipes from Google Sheets into FoodieFix database.
"""

import json
import os
import sys
from typing import Any, Dict, List

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from tqdm import tqdm

# Add parent directory to path so we can import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.scraping.recipe_scraper import EliteRecipeScraper

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_google_creds() -> Credentials:
    """Get Google API credentials."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def get_sheet_data(spreadsheet_id: str, range_name: str) -> List[List[str]]:
    """Get data from Google Sheet."""
    creds = get_google_creds()
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    )
    return result.get("values", [])


def import_recipes(
    spreadsheet_id: str, range_name: str, user_id: str
) -> Dict[str, Any]:
    """Import recipes from Google Sheet into database."""
    print("Fetching URLs from Google Sheet...")
    rows = get_sheet_data(spreadsheet_id, range_name)

    if not rows:
        print("No data found.")
        return {"success": 0, "failed": 0, "errors": []}

    # Initialize scraper
    scraper = EliteRecipeScraper()
    results = {"success": 0, "failed": 0, "errors": []}

    print(f"\nFound {len(rows)} recipes to import")
    for row in tqdm(rows, desc="Importing recipes"):
        try:
            url = row[0]  # Assuming URL is in first column
            recipe_data = scraper.scrape(url)

            # TODO: Insert into FoodieFix database
            # This will depend on your database setup

            results["success"] += 1

        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"url": url, "error": str(e)})

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import recipes from Google Sheet")
    parser.add_argument("spreadsheet_id", help="Google Sheet ID")
    parser.add_argument("range", help="Sheet range (e.g. Sheet1!A2:A)")
    parser.add_argument("user_id", help="FoodieFix user ID")
    args = parser.parse_args()

    results = import_recipes(args.spreadsheet_id, args.range, args.user_id)
    print("\nImport complete!")
    print(f"Successfully imported: {results['success']}")
    print(f"Failed: {results['failed']}")
    if results["failed"] > 0:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"- {error['url']}: {error['error']}")
