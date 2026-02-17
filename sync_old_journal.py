import os
import json
import urllib.request
from pathlib import Path

TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"

def get_access_token():
    with open(TOKEN_FILE) as f:
        tokens = json.load(f)
    return tokens['access_token']

def append_rows(spreadsheet_id, range_name, values):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}:append?valueInputOption=USER_ENTERED"
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }
    body = json.dumps({"values": values}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Data from Sheet 1 (Income)
income_data = [
    ['2025-07-25', 'Adrian Singh', 'Liverpool cleaning', '69.75', 'Bank Transfer'],
    ['2025-07-28', 'Rebecca Tom', 'Invoice-1 Luxe and Co', '265', 'Bank Transfer', 'INV-1'],
    ['2025-07-31', 'Adrian Singh', 'Apartment Cleaning 1108', '209.25', 'Bank Transfer'],
    ['2025-08-04', 'Rebecca Tom', 'Gurpreet clean Saturday', '55', 'Bank Transfer'],
    ['2025-08-16', 'Mivaan Nesakumar', '17 Boab Place, Casula', '156.25', 'Bank Transfer'],
    ['2025-08-22', 'Mivaan Nesakumar', '17 Boab Place, Casula', '500', 'Bank Transfer'],
    ['2025-08-24', 'Recovery N Care Pty Ltd', 'Invoice 01', '655', 'Bank Transfer', 'INV-01'],
    ['2025-08-28', 'Mivaan Nesakumar', 'U49/81 Memorial Ave', '95', 'Bank Transfer'],
    ['2025-09-01', 'Recovery N Care Pty Ltd', 'Invoice 2', '826', 'Bank Transfer', 'INV-02'],
    ['2025-09-01', 'Mivaan Nesakumar', '49/81 Memorial Ave', '285', 'Bank Transfer'],
    ['2025-09-04', 'Rochelle Anjaiya', 'Sep 25 cleaning', '350', 'Bank Transfer'],
    ['2025-09-09', 'Recovery N Care Pty Ltd', 'Invoice 3', '812.5', 'Bank Transfer', 'INV-03'],
    ['2025-09-10', 'Van Thong Nguyen', 'Cleaning 660', '110', 'Bank Transfer'],
    ['2025-09-14', 'Recovery N Care Pty Ltd', 'Invoice 004', '845', 'Bank Transfer', 'INV-04'],
    ['2025-09-20', 'Anita J Forte', 'Cleaning', '20', 'Bank Transfer'],
    ['2025-10-07', 'Rochelle Anjaiya', '2 Amanda Close DP', '160', 'Bank Transfer'],
    ['2025-10-12', 'Hinarii', 'Cleaning', '50', 'Bank Transfer'],
    ['2025-10-12', 'Faraz Ahmed', 'End of lease clean', '162.5', 'Bank Transfer'],
    ['2025-10-13', 'T L Cross / M J Greenwood', 'Cleaning 12 West St', '300', 'Bank Transfer'],
    ['2025-10-14', 'Thomas Jochinger', '4/4 Mary St Deposit', '50', 'Bank Transfer'],
    ['2025-10-15', 'Shayal P Prasad', '25% deposit deep clean', '125', 'Bank Transfer'],
    ['2025-10-16', 'Tanisha A Kumar', 'Cleaning', '100', 'Bank Transfer'],
    ['2025-10-17', 'Mandeep Kaur', '13 Mary Crescent cleaning', '95', 'Bank Transfer'],
    ['2025-10-17', 'Thomas Jochinger', '4/4 Mary St Balance', '150', 'Bank Transfer'],
    ['2025-10-19', 'Revin Talisic', 'House cleaning deposit', '150', 'Bank Transfer'],
    ['2025-10-21', 'Amina Alalikin', 'Cleaning', '20', 'Bank Transfer'],
    ['2025-10-21', 'Revin Talisic', 'House cleaning balance', '450', 'Bank Transfer'],
    ['2025-10-24', 'Mohammad Ahmed', 'Faraz Schofields cleaning', '487', 'Bank Transfer'],
    ['2025-11-03', 'Nayyar Ghaznavi', 'Cleaning', '160', 'Bank Transfer'],
    ['2025-11-05', 'Mrs Shayan S Chand', 'Cleaning', '150', 'Bank Transfer'],
    ['2025-11-09', 'Amina Alalikin', 'Cleaning', '150', 'Bank Transfer'],
    ['2025-11-10', 'Rochelle Anjaiya', 'Rochelle clean', '160', 'Bank Transfer'],
    ['2025-11-11', 'Corey William Lake', 'Cleaning', '125', 'Bank Transfer'],
    ['2025-11-14', 'Mrs Shayan S Chand', 'Cleaning', '160', 'Bank Transfer'],
    ['2025-11-21', 'Natalie Saab', '10 Lightwood St', '125', 'Bank Transfer'],
    ['2025-11-24', 'Corey William Lake', 'Cleaning', '425', 'Bank Transfer'],
    ['2025-11-25', 'Razia Ghaznavi', 'Cleaning', '120', 'Bank Transfer'],
    ['2025-11-28', 'Mrs Shayan S Chand', 'Sha cleaning', '160', 'Bank Transfer'],
    ['2025-12-04', 'Amina Alalikin', 'Apartment cleaning', '280', 'Bank Transfer'],
    ['2025-12-05', 'Mohammed Iqbal', 'MIA cleaning', '150', 'Bank Transfer'],
    ['2025-12-19', 'Mrs Shayan S Chand', 'Sha cleaning', '160', 'Bank Transfer'],
    ['2025-12-21', 'Priya Prikashni Chand', 'Casula cleaning', '120', 'Bank Transfer'],
    ['2025-12-22', 'Cash Deposit', 'Cleaning payment (cash)', '280', 'Cash'],
    ['2025-12-24', 'Cash Deposit', 'Cleaning payment (cash)', '250', 'Cash'],
    ['2025-08-23', 'Karan Boss', 'CUB-16/08 Australia Post', '120', 'Square', '#CUB-16/08'],
    ['2025-10-25', 'Faraz Ahmed', 'End of lease Schofields', '650', 'Square', '#000001'],
    ['2025-12-30', 'Herdip Gill', 'Cub-Airb-001', '1160', 'Square', '#Cub-Airb-001'],
    ['2026-01-02', 'Shayan Chand', 'Cleaning', '160', 'Square', '#000004'],
    ['2025-09-29', 'Nayyar Ghaznavi', 'Cleaning', '160', 'Bank Transfer (ANZ)']
]

# Map income to Master Ops Client%20Log format:
# [Date, Client Name, Phone, Email, Service Type, Location/Suburb, Quote Amount, Invoice #, Payment Status, Amount Paid, Source, Notes]
formatted_income = []
for row in income_data:
    date = row[0]
    client = row[1]
    desc = row[2]
    amount = row[3]
    source = row[4]
    inv = row[5] if len(row) > 5 else ''
    formatted_income.append([date, client, '', '', desc, '', amount, inv, 'Paid', amount, source, 'Imported from old journal'])

# Data from Sheet 2 (Expenses)
expense_data = [
    ['2025-06-30', 'Go Daddy - Domain', 'Website/Marketing', '50', 'Bank Transfer'],
    ['2025-06-30', 'Cleaning business setup', 'Business Setup', '15.91', 'Bank Transfer'],
    ['2025-06-30', 'Business card printing', 'Marketing', '21.38', 'Bank Transfer'],
    ['2025-07-02', 'Bunnings - cleaning equipment', 'Equipment/Supplies', '490.62', 'Card'],
    ['2025-07-02', 'Officeworks', 'Office Supplies', '8.58', 'Card'],
    ['2025-07-03', 'Cleaning business supplies', 'Supplies', '32', 'Bank Transfer'],
    ['2025-07-19', 'Bunnings - supplies', 'Equipment/Supplies', '78.4', 'Card'],
    ['2025-07-22', 'Officeworks', 'Office Supplies', '62.68', 'Card'],
    ['2025-07-25', 'WWC NSW check', 'Compliance', '100', 'Bank Transfer'],
    ['2025-07-27', 'Bunnings - supplies', 'Equipment/Supplies', '33.49', 'Card'],
    ['2025-07-29', 'Service NSW - business', 'Compliance', '107', 'Card'],
    ['2025-07-29', 'NRMA Insurance', 'Insurance', '64.8', 'Card'],
    ['2025-07-29', 'Officeworks', 'Office Supplies', '19.34', 'Card'],
    ['2025-08-13', 'LinkedIn Premium', 'Marketing', '31', 'Bank Transfer'],
    ['2025-08-14', 'Cleaning detergents', 'Supplies', '50', 'Bank Transfer'],
    ['2025-08-24', 'Cleaning website', 'Website/Marketing', '65', 'Bank Transfer'],
    ['2025-08-27', 'Square subscription', 'Payment Processing', '27.1', 'Card'],
    ['2025-08-29', 'Bunnings - supplies', 'Equipment/Supplies', '179.2', 'Card'],
    ['2025-08-29', 'Cleaning business supplies', 'Supplies', '180', 'Bank Transfer'],
    ['2025-09-02', 'Bunnings - supplies', 'Equipment/Supplies', '179.2', 'Card'],
    ['2025-10-07', 'Cleaning detergent', 'Supplies', '73', 'Bank Transfer'],
    ['2025-10-09', 'Bunnings - supplies', 'Equipment/Supplies', '53.03', 'Card'],
    ['2025-10-17', 'Cleaning detergent', 'Supplies', '48', 'Bank Transfer'],
    ['2025-10-21', 'Cleaning products', 'Supplies', '76', 'Bank Transfer'],
    ['2025-10-23', 'Bunnings - supplies', 'Equipment/Supplies', '77', 'Card'],
    ['2025-10-24', 'Carpet steamer rental', 'Equipment Rental', '150', 'Bank Transfer'],
    ['2025-11-03', 'Cleaning supplies', 'Supplies', '20', 'Bank Transfer'],
    ['2025-11-05', 'Framer.com - website', 'Website/Marketing', '16.5', 'Card'],
    ['2025-11-05', 'Cleaning supplies', 'Supplies', '15', 'Bank Transfer'],
    ['2025-11-06', 'Apify subscription', 'Software/Tools', '9.21', 'Card'],
    ['2025-11-06', 'Cleaning detergent', 'Supplies', '20', 'Bank Transfer'],
    ['2025-11-07', 'Cleaning supplies', 'Supplies', '25', 'Bank Transfer'],
    ['2025-11-12', 'Facebook ad', 'Marketing', '15', 'Bank Transfer'],
    ['2025-11-19', 'Uber for Larissa (client)', 'Transport', '70', 'Bank Transfer'],
    ['2025-11-20', 'First Aid Certificate', 'Training/Compliance', '110', 'Card'],
    ['2025-11-25', 'Linkt tolls', 'Transport', '22.44', 'Card'],
    ['2025-11-27', 'Linkt tolls', 'Transport', '9.29', 'Card'],
    ['2025-12-04', 'Grade car rentals', 'Vehicle', '166', 'Bank Transfer'],
    ['2025-12-19', 'Cleaning detergent', 'Supplies', '30', 'Bank Transfer'],
    ['2025-12-24', 'Linkt tolls', 'Transport', '20.07', 'Card'],
    ['2025-06-30', 'Fuel - business portion (60%)', 'Fuel', '24', 'Card'],
    ['2025-07-18', 'Fuel - business portion (60%)', 'Fuel', '27.88', 'Card'],
    ['2025-07-26', 'Fuel - business portion (60%)', 'Fuel', '96', 'Bank Transfer'],
    ['2025-07-31', 'Fuel - business portion (60%)', 'Fuel', '31.8', 'Bank Transfer'],
    ['2025-08-05', 'Fuel - business portion (60%)', 'Fuel', '30', 'Card'],
    ['2025-09-06', 'Fuel - business portion (60%)', 'Fuel', '40.8', 'Card'],
    ['2025-10-16', 'Fuel - business portion (60%)', 'Fuel', '20.1', 'Card'],
    ['2025-10-18', 'Fuel - business portion (60%)', 'Fuel', '35.33', 'Card'],
    ['2025-10-24', 'Fuel - business portion (60%)', 'Fuel', '36', 'Bank Transfer'],
    ['2025-11-05', 'Fuel - business portion (60%)', 'Fuel', '15', 'Card'],
    ['2025-11-25', 'Fuel - business portion (60%)', 'Fuel', '24', 'Card'],
    ['2025-12-16', 'Fuel - business portion (60%)', 'Fuel', '30', 'Card']
]

# Map expenses to Master Ops Bookkeeping format:
# [Date, Description, Category, Amount, Payment Method, GST (1/11), Net Amount]
formatted_expenses = []
for row in expense_data:
    date = row[0]
    desc = row[1]
    cat = row[2]
    amount = float(row[3])
    method = row[4]
    gst = round(amount / 11, 2)
    net = round(amount - gst, 2)
    formatted_expenses.append([date, desc, cat, amount, method, gst, net])

MASTER_OPS_ID = "1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU"
FINANCE_BACKUP_ID = "1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q"

# Append to Master Ops - Client%20Log
append_rows(MASTER_OPS_ID, "Client%20Log!A:L", formatted_income)
# Append to Master Ops - Bookkeeping
append_rows(MASTER_OPS_ID, "Bookkeeping!A:G", formatted_expenses)

print("Migration complete.")
