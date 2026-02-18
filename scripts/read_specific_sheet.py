#!/usr/bin/env python3
import sys
import os
from google_sheets_api import GoogleSheetsAPI

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 read_specific_sheet.py <spreadsheet_id> <range>")
        sys.exit(1)
    
    ss_id = sys.argv[1]
    range_str = sys.argv[2]
    
    gs = GoogleSheetsAPI(spreadsheet_id=ss_id)
    try:
        info = gs.info()
        if "error" in info:
            print(f"Info Error: {info['error']}")
        else:
            sheets = [s["properties"]["title"] for s in info.get("sheets", [])]
            print(f"Available sheets: {', '.join(sheets)}")
        
        rows = gs.read(range_str)
        if not rows:
            print("(empty)")
        else:
            for row in rows:
                print(" | ".join(str(c) for c in row))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
