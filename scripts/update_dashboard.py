import json
import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_FILE = os.path.join(BASE_DIR, "memory/working/current-tasks.json")
METRICS_FILE = os.path.join(BASE_DIR, "memory/working/metrics.json")
OUTPUT_JS = os.path.join(BASE_DIR, "dashboard/dashboard-data.js")

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def run():
    print("🧠 Bella Memory Bridge: Syncing dashboard data...")
    
    tasks_data = load_json(TASKS_FILE)
    metrics_data = load_json(METRICS_FILE)
    
    # Map active_tasks to Kanban columns
    def get_icon(desc):
        desc = desc.lower()
        if "llm" in desc or "claude" in desc or "ai" in desc: return "🤖"
        if "sync" in desc or "dashboard" in desc: return "💾"
        if "invoice" in desc or "payment" in desc or "$" in desc: return "💰"
        if "structure" in desc or "folder" in desc: return "📂"
        if "larissa" in desc: return "👩‍⚕️"
        if "airbnb" in desc or "unit 4" in desc: return "🏠"
        if "clean" in desc: return "✨"
        return "📄"

    todo = []
    in_progress = []
    done = []
    
    for task in tasks_data.get("active_tasks", []):
        status = task.get("status", "pending")
        desc = task.get("description", "")
        item = {
            "id": task.get("id"),
            "title": desc,
            "priority": task.get("priority", "medium"),
            "tag": task.get("category", "General"),
            "icon": get_icon(desc)
        }
        
        if status == "pending":
            todo.append(item)
        elif status == "in_progress":
            in_progress.append(item)
        elif status == "completed":
            done.append(item)
            
    # Add today's completed items to 'done'
    for completed_desc in tasks_data.get("completed_today", []):
        done.append({
            "id": "c-" + str(hash(completed_desc))[:6],
            "title": completed_desc,
            "tag": "Completed",
            "priority": "low",
            "icon": get_icon(completed_desc)
        })

    # Prepare final payload
    payload = {
        "lastUpdated": datetime.now().isoformat(),
        "updatedBy": "Bella Neural Engine",
        "system_state": "ACTIVE",
        "stats": {
            "totalRevenue": metrics_data.get("business", {}).get("total_revenue", 0),
            "netProfit": metrics_data.get("business", {}).get("net_profit", 0),
            "outstanding": metrics_data.get("business", {}).get("outstanding_invoices", 0),
            "overdueCount": metrics_data.get("business", {}).get("overdue_count", 0),
            "revenueChange": f"+{metrics_data.get('business', {}).get('revenue_change_pct', 0)}%",
            "profitMargin": f"{metrics_data.get('business', {}).get('profit_margin', 0)}%"
        },
        "tasks": {
            "todo": todo,
            "in_progress": in_progress,
            "done": done
        },
        "bella": {
            "model": "Claude 3.5 Sonnet",
            "avatar": "assets/bella-goddess-2026-02-14.png",
            "soul_frequency": "1.2Hz"
        }
    }
    
    # Write to JS file
    with open(OUTPUT_JS, 'w') as f:
        f.write("window.dashboardData = ")
        json.dump(payload, f, indent=2)
        
    print(f"✅ Dashboard sync complete! Saved to {OUTPUT_JS}")

if __name__ == "__main__":
    run()
