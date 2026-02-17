import json
import os

DASHBOARD_PATH = "dashboard-data.json"

def update_dashboard(task_name, status, notes=""):
    if not os.path.exists(DASHBOARD_PATH):
        data = {"liveTasks": [], "stats": {}, "bella": {}}
    else:
        with open(DASHBOARD_PATH, "r") as f:
            data = json.load(f)

    updated = False
    for task in data.get("liveTasks", []):
        if task["name"] == task_name:
            task["status"] = status
            task["notes"] = notes
            updated = True
            break
    
    if not updated:
        data.setdefault("liveTasks", []).append({
            "name": task_name,
            "status": status,
            "notes": notes
        })

    with open(DASHBOARD_PATH, "w") as f:
        json.dump(data, f, indent=2)

update_dashboard("Connecteam Dashboard Overhaul", "In Progress", "Updating staff bios and branding.")
