from tinydb import TinyDB, Query
from datetime import datetime
from utility import truncate

db = TinyDB("ledger.json", indent=3)
q = Query()

ledger = db.table("ledger")
assets = db.table("assets")
tab = db.table("tab")
history = db.table("history")


class Tab:
    def add_associate(name, associate_id, initial_debt=0):
        tab.insert({
            "name": name,
            "debt": initial_debt,
            "id": associate_id,
        })
        History.document(f"New associate {name}" + (f" (${initial_debt} debt)" if initial_debt else ""), "tab")

    def count():
        return len(tab.all())

    def get_all():
        return tab.all()

    def remove_associate(associate_id):
        associate = Tab.find(associate_id)
        if not associate:
            return False
        
        tab.remove(q.id == associate_id)
        History.document(f"Removed associate {associate['name']}", "tab")
        return True

    def find(identifier):
        key = identifier.strip().lower()
        for entry in tab.all():
            if entry["name"].lower() == key or entry["id"].lower() == key:
                return entry
        return None

    def update_debt(associate_id, amount, reason, mode):
        associate = Tab.find(associate_id)
        old_debt =  associate["debt"]
        new_debt = {"add": old_debt + amount, "remove": old_debt - amount, "set": amount}[mode]
        tab.update({"debt": new_debt}, q.id == associate_id)
    
        logs = {
            "add": f"owes -${amount}", 
            "remove": f"paid off +${amount}", 
            "set": f"debt set to ${amount}"
        }

        History.document(f"{associate['name']} {logs[mode]} ({reason})", "tab")
        return new_debt, old_debt


class Assets:
    def add_asset(name, asset_id, unit, display_image="", initial_stock=0):
        assets.insert({
            "name": name,
            "unit": unit,
            "stock": initial_stock,
            "display_image": display_image,
            "id": asset_id,
        })
        History.document(f"New asset {name}" + (f" ({int(initial_stock)}{unit}(s) stock)" if initial_stock else ""), "assets")

    def count():
        return len(assets.all())

    def get_all():
        return assets.all()

    def remove_asset(asset_id):
        asset = Assets.find(asset_id)
        if not asset:
            return False
        assets.remove(q.id == asset_id)
        History.document(f"Removed asset {asset['name']}", "assets")
        return True

    def find(identifier):
        key = identifier.strip().lower()
        for entry in assets.all():
            if entry["name"].lower() == key or entry["id"].lower() == key:
                return entry
        return None

    def update_settings(asset_id, name, unit, display_image):
        asset = Assets.find(asset_id)
        assets.update({"name": name, "unit": unit, "display_image": display_image}, q.id == asset_id)
        History.document(f"Updated settings for {asset['name']}", "assets")

    def update_stock(asset_id, amount, reason, mode):
        asset = Assets.find(asset_id)
        old_stock = asset["stock"]
        new_stock = {"add": old_stock + amount, "remove": old_stock - amount, "set": amount}[mode]
        assets.update({"stock": new_stock}, q.id == asset_id)
        display_amount = f"{int(amount)({asset['unit']})}(s)"

        logs = {
            "add": f"+{display_amount}",
            "remove": f"-{display_amount}",
            "set": f"stock set to {display_amount}"
        }

        History.document(f"Stock change {asset['name']} {logs[mode]} ({reason})", "assets")
        return new_stock, old_stock


class Balance:
    def update(amount, reason, mode):
        old_bal = ledger.all()[0]["balance"]
        new_bal = {"add": old_bal + amount, "remove": old_bal - amount, "set": amount}[mode]
        ledger.update({"balance": new_bal})

        logs = {
            "add": f"Gained +${amount}",
            "remove": f"Lost -${amount}",
            "set": f"Set ${amount}"
        }

        History.document(f"{logs[mode]} Balance ({reason})", "balance")
        return new_bal, old_bal

    def get():
        return ledger.all()[0]["balance"]

    def predict():
        return Balance.get() + sum(a["debt"] for a in tab.all())
    

class History:
    def document(event, etype):
        now = datetime.now()
        history.insert({
            "event": event,
            "type": etype,
            "date": now.strftime("%m/%d/%H:%M"),
        })

    def export():
        entries = history.all()
        if not entries:
            return "No history."
        lines = []
        for entry in entries:
            lines.append(f"{entry['date']} | [{entry['type']}] {entry['event']}")
        return "\n".join(lines)

    def format(limit=7, compact=False):
        entries = history.all()[-limit:]
        entries.reverse()
        if not entries:
            return "```\nNo history.\n```"
        lines = []
        for entry in entries:
            lines.append(f"{entry['date']} | {compact and entry['event'] or truncate(entry['event'])}")
        return "```\n" + "\n".join(lines) + "\n```"


class Ledger:
    def read():
        return ledger.all()[0]
    
    def wipe():
        ledger.truncate()
        assets.truncate()
        tab.truncate()
        history.truncate()
        Ledger.init()

    def init():
        if not ledger.all():
            ledger.insert({
                "balance": 0
            })