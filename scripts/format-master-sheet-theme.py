#!/usr/bin/env python3
"""
Apply high-color formatting theme to Master Ops sheet.
"""

import argparse

from google_sheets_api import GoogleSheetsAPI

MASTER_ID = "1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU"


def rgb(r: int, g: int, b: int) -> dict:
    return {"red": r / 255, "green": g / 255, "blue": b / 255}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sheet-id", default=MASTER_ID)
    args = p.parse_args()

    gs = GoogleSheetsAPI(spreadsheet_id=args.sheet_id)
    meta = gs.info()
    sheets = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta.get("sheets", [])}

    style_map = {
        "Client Log": rgb(26, 115, 232),
        "Bookkeeping": rgb(67, 160, 71),
        "Expenses": rgb(251, 140, 0),
        "Airbnb Cleans": rgb(142, 36, 170),
        "Non-Airbnb Jobs": rgb(0, 137, 123),
        "Staff & Wages": rgb(121, 85, 72),
        "P&L Summary": rgb(233, 30, 99),
        "SOT_Dashboard": rgb(63, 81, 181),
        "SOT_Health": rgb(0, 150, 136),
        "Sync_Errors": rgb(198, 40, 40),
    }

    requests = []
    for name, color in style_map.items():
        sid = sheets.get(name)
        if sid is None:
            continue
        # Freeze header
        requests.append(
            {
                "updateSheetProperties": {
                    "properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1}},
                    "fields": "gridProperties.frozenRowCount",
                }
            }
        )
        # Header style A1:Z1
        requests.append(
            {
                "repeatCell": {
                    "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 26},
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": color,
                            "textFormat": {"bold": True, "foregroundColor": rgb(255, 255, 255)},
                            "horizontalAlignment": "CENTER",
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
                }
            }
        )

    # Conditional formatting for Client Log status column I
    sid = sheets.get("Client Log")
    if sid is not None:
        requests.extend(
            [
                {
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [{"sheetId": sid, "startRowIndex": 1, "startColumnIndex": 8, "endColumnIndex": 9}],
                            "booleanRule": {
                                "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "Overdue"}]},
                                "format": {"backgroundColor": rgb(255, 235, 238), "textFormat": {"bold": True, "foregroundColor": rgb(183, 28, 28)}},
                            },
                        },
                        "index": 0,
                    }
                },
                {
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [{"sheetId": sid, "startRowIndex": 1, "startColumnIndex": 8, "endColumnIndex": 9}],
                            "booleanRule": {
                                "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "Paid"}]},
                                "format": {"backgroundColor": rgb(232, 245, 233), "textFormat": {"bold": True, "foregroundColor": rgb(27, 94, 32)}},
                            },
                        },
                        "index": 0,
                    }
                },
            ]
        )

    # Sync_Errors color accents
    sid_err = sheets.get("Sync_Errors")
    if sid_err is not None:
        requests.append(
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{"sheetId": sid_err, "startRowIndex": 1, "startColumnIndex": 2, "endColumnIndex": 3}],
                        "booleanRule": {
                            "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "FAIL"}]},
                            "format": {"backgroundColor": rgb(255, 205, 210), "textFormat": {"bold": True}},
                        },
                    },
                    "index": 0,
                }
            }
        )

    if requests:
        gs.batch_update_spreadsheet(requests)
    print(f"Applied theme updates with {len(requests)} requests to {args.sheet_id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
