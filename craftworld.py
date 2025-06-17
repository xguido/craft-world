import json
import uuid
import requests
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class Logger:
    @staticmethod
    def step(msg): console.print(f"[bold cyan]🌀 {msg}[/]")
    @staticmethod
    def info(msg): console.print(f"[green]✅ {msg}[/]")
    @staticmethod
    def warn(msg): console.print(f"[yellow]⚠️  {msg}[/]")
    @staticmethod
    def action(msg): console.print(f"[white]🚀 {msg}[/]")
    @staticmethod
    def error(msg): console.print(f"[red]❌ {msg}[/]")
    @staticmethod
    def watermark(): console.print(Panel("💠 [bold magenta]LYAMRIZZ INSIDER By ROBI[/bold magenta]", expand=False))

def read_tokens():
    try:
        with open('token.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        Logger.error(f"Gagal baca token.txt: {e}")
        return []

def read_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        Logger.error(f"Gagal baca config.json: {e}")
        return {}

def get_headers(token):
    if not token.startswith("jwt_"):
        token = f"jwt_{token}"
    return {
        "accept": "*/*",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "x-app-version": "0.33.9",
        "Referer": "https://preview.craft-world.gg/"
    }

def post_action(token, action_type, payload):
    url = "https://preview.craft-world.gg/api/1/user-actions/ingest"
    headers = get_headers(token)
    data = {
        "data": [{
            "id": str(uuid.uuid4()),
            "actionType": action_type,
            "payload": payload,
            "time": int(time.time() * 1000)
        }]
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        return res.json().get("data", {}).get("account", None)
    except requests.exceptions.HTTPError as e:
        if res.status_code == 500:
            Logger.warn(f"{action_type} gagal (mungkin belum bisa dilakukan).")
        else:
            Logger.error(f"Gagal {action_type}: {e}")
        return None
    except Exception as e:
        Logger.error(f"Gagal {action_type}: {e}")
        return None

def handle_earth_mine(token, mine_id):
    Logger.action("START_MINE...")
    account = post_action(token, "START_MINE", {"mineId": mine_id})
    if not account:
        Logger.warn("START_MINE gagal. Coba CLAIM_MINE...")
        account = post_action(token, "CLAIM_MINE", {"mineId": mine_id})
    return account

def start_factory(token, factory_id, label):
    Logger.action(f"START_FACTORY {label} (ID: {factory_id})...")
    return post_action(token, "START_FACTORY", {"factoryId": factory_id})

def upgrade_mine(token, mine_id):
    Logger.action(f"UPGRADE_MINE (ID: {mine_id})...")
    return post_action(token, "UPGRADE_MINE", {"mineId": mine_id})

def upgrade_factory(token, factory_id, label):
    Logger.action(f"UPGRADE_FACTORY {label} (ID: {factory_id})...")
    return post_action(token, "UPGRADE_FACTORY", {"factoryId": factory_id})

def handle_claim_area(token, area_id, account, index, resource):
    Logger.action(f"CLAIM_AREA {resource}...")
    amount = 9999
    new_account = post_action(token, "CLAIM_AREA", {"areaId": area_id, "amountToClaim": amount})
    if new_account:
        Logger.info(f"CLAIM_AREA {resource} berhasil!")
        return new_account
    else:
        Logger.warn(f"CLAIM_AREA {resource} gagal.")
        return account

def show_account_info(index, account):
    table = Table(title=f"🧑‍🌾 Akun {index + 1}: {account.get('walletAddress')}", show_lines=True)
    table.add_column("Parameter", style="cyan", justify="right")
    table.add_column("Value", style="magenta", justify="left")

    table.add_row("XP", f"{account.get('experiencePoints', 0):,}")
    table.add_row("Power", f"{account.get('power', 0):,}")
    table.add_row("Skill Points", f"{account.get('skillPoints', 0):,}")
    power_ms = account.get("powerMillisecondsUntilRefill", 0)
    refill_info = f"{power_ms // 1000} detik" if power_ms > 0 else "Penuh / belum aktif"
    table.add_row("Power Refill", refill_info)

    resources = account.get("resources", [])
    for r in resources:
        if r["amount"] > 0:
            table.add_row(f"{r['symbol']}", f"{r['amount']:,}")

    console.print(table)
    Logger.watermark()

def main():
    while True:
        Logger.step("🔄 Memulai siklus baru...")
        tokens = read_tokens()
        config = read_config()

        if not tokens:
            Logger.error("Tidak ada token ditemukan.")
            return

        for i, token in enumerate(tokens):
            mine_id = config.get(f"mineId_{i+1}")
            factory_mud = config.get(f"factoryMud_{i+1}", [])
            factory_clay = config.get(f"factoryClay_{i+1}", [])
            factory_sand = config.get(f"factorySand_{i+1}", [])
            area_mud = config.get(f"areaId_{i+1}")
            area_clay = config.get(f"areaClay_{i+1}")
            area_sand = config.get(f"areaSand_{i+1}")

            if not isinstance(factory_mud, list): factory_mud = [factory_mud]
            if not isinstance(factory_clay, list): factory_clay = [factory_clay]
            if not isinstance(factory_sand, list): factory_sand = [factory_sand]

            if not mine_id:
                Logger.error(f"mineId untuk akun {i+1} tidak ditemukan.")
                continue

            account = handle_earth_mine(token, mine_id)
            if not account:
                Logger.error(f"Gagal START/CLAIM MINE akun {i+1}")
                continue

            if config.get(f"upgradeMine_{i+1}", False):
                account = upgrade_mine(token, mine_id) or account

            if config.get(f"upgradeFactoryMud_{i+1}", False):
                for fid in factory_mud:
                    account = upgrade_factory(token, fid, "MUD") or account
            if config.get(f"upgradeFactoryClay_{i+1}", False):
                for fid in factory_clay:
                    account = upgrade_factory(token, fid, "CLAY") or account
            if config.get(f"upgradeFactorySand_{i+1}", False):
                for fid in factory_sand:
                    account = upgrade_factory(token, fid, "SAND") or account

            for fid in factory_mud:
                account = start_factory(token, fid, "MUD") or account
            for fid in factory_clay:
                account = start_factory(token, fid, "CLAY") or account
            for fid in factory_sand:
                account = start_factory(token, fid, "SAND") or account

            if area_mud:
                account = handle_claim_area(token, area_mud, account, i, "MUD") or account
            if area_clay:
                account = handle_claim_area(token, area_clay, account, i, "CLAY") or account
            if area_sand:
                account = handle_claim_area(token, area_sand, account, i, "SAND") or account

            show_account_info(i, account)

        Logger.step("⏳ Menunggu 30 detik sebelum siklus berikutnya...\n")
        time.sleep(30)

if __name__ == "__main__":
    main()
