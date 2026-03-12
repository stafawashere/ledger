from tinydb import TinyDB, Query
from datetime import datetime
from utility import truncate, fmt_num

db = TinyDB("ledger.json", indent=3)
q = Query()

ledger = db.table("ledger")
assets = db.table("assets")
tab = db.table("tab")
history = db.table("history")


class Tab:
    def add_associate(name, associate_id, initial_debt=0):
        if Tab.find(associate_id):
            return False
        tab.insert({
            "name": name,
            "debt": initial_debt,
            "id": associate_id,
        })
        History.document(f"New associate {name}" + (f" (${initial_debt} debt)" if initial_debt else ""), "tab")
        return True

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
        if not identifier:
            return None
        key = identifier.strip().lower()
        for entry in tab.all():
            if entry["name"].lower() == key or entry["id"].lower() == key:
                return entry
        return None

    def update_debt(associate_id, amount, reason, mode):
        associate = Tab.find(associate_id)
        if not associate:
            return None, None
        old_debt = associate["debt"]
        new_debt = {"add": old_debt + amount, "remove": old_debt - amount, "set": amount}[mode]
        tab.update({"debt": new_debt}, q.id == associate_id)

        logs = {
            "add": f"incurred +${amount}",
            "remove": f"paid off ${amount}",
            "set": f"debt set to ${amount}"
        }

        History.document(f"{associate['name']} {logs[mode]} ({reason})", "tab")
        return new_debt, old_debt


class Assets:
    def add_asset(name, asset_id, unit, display_image="", initial_stock=0):
        if Assets.find(asset_id):
            return False
        assets.insert({
            "name": name,
            "unit": unit,
            "stock": initial_stock,
            "display_image": display_image,
            "id": asset_id,
        })
        History.document(f"New asset {name}" + (f" ({fmt_num(initial_stock)} {unit}(s) stock)" if initial_stock else ""), "assets")
        return True

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
        if not identifier:
            return None
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
        if not asset:
            return None, None
        old_stock = asset["stock"]
        new_stock = {"add": old_stock + amount, "remove": old_stock - amount, "set": amount}[mode]
        assets.update({"stock": new_stock}, q.id == asset_id)
        display_amount = f"{fmt_num(amount)} {asset['unit']}(s)"

        logs = {
            "add": f"+{display_amount}",
            "remove": f"-{display_amount}",
            "set": f"set to {display_amount}"
        }

        History.document(f"Stock change {asset['name']} {logs[mode]} ({reason})", "assets")
        return new_stock, old_stock


class Balance:
    def update(amount, reason, mode):
        bal = ledger.all()
        if not bal:
            Ledger.init()
            bal = ledger.all()
        old_bal = bal[0]["balance"]
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
        bal = ledger.all()
        if not bal:
            Ledger.init()
            return 0
        return bal[0]["balance"]

    def owed():
        return sum(a["debt"] for a in tab.all())


class History:
    def document(event, etype):
        now = datetime.now()
        history.insert({
            "event": event,
            "type": etype,
            "date": now.strftime("%m/%d/%H:%M"),
        })

    def export(limit=0, format=False, compact=False, compactness=42, inclusion=None):
        entries = history.all()

        if inclusion:
            entries = [e for e in entries if any(
                s.lower() in e['event'].lower() or s.lower() == e['type'].lower() for s in inclusion
            )]

        if limit:
            entries = entries[-limit:]

        entries.reverse()

        if not entries:
            return "```\nNo history.\n```" if format else "No history."

        lines = []
        for entry in entries:
            event = truncate(entry['event'], compactness) if compact else entry['event']
            prefix = f"{entry['date']} | " if compact else f"{entry['date']} | [{entry['type']}] "
            lines.append(f"{prefix}{event}")

        output = "\n".join(lines)
        return f"```\n{output}\n```" if format else output


class Ledger:
    def read():
        bal = ledger.all()
        if not bal:
            Ledger.init()
            return ledger.all()[0]
        return bal[0]

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