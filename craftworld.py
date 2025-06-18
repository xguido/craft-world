import json
import uuid
import requests
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

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

def read_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        Logger.error(f"Gagal baca config.json: {e}")
        return {}

account_tokens = {}

def fetch_token(api_key, refresh_token):
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://preview.craft-world.gg",
        "priority": "u=1, i",
        "referer": "https://preview.craft-world.gg/",
        "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    try:
        res = requests.post(url, headers=headers, data=data)
        res.raise_for_status()
        return res.json().get("access_token")
    except Exception as e:
        Logger.error(f"Failed to fetch token: {e}")
        return None

def get_account_token(account_index, api_key, refresh_token):
    now = time.time()
    token_info = account_tokens.get(account_index)
    if token_info and now < token_info['expires_at']:
        return token_info['token']
    token = fetch_token(api_key, refresh_token)
    if token:
        account_tokens[account_index] = {'token': token, 'expires_at': now + 1800}
        return token
    else:
        return None

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
    except Exception as e:
        Logger.error(f"Gagal {action_type}: {e}")
        return None

def fetch_graphql_data(token):
    url = "https://preview.craft-world.gg/graphql"
    query = """
    query AggregatedCraftWorldDataQuery {
        account {
            id
            mines { id definition { id } }
            landPlots {
                id name areas { id symbol landPlotId landPlotPosition factories { factory { id level definition { id } } } }
            }
        }
    }
    """
    headers = get_headers(token)
    payload = { "query": query }
    try:
        res = requests.post(url, json=payload, headers=headers)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        Logger.error(f"Failed to fetch GraphQL: {e}")
        return None

def extract_and_update_config(graphql_data, config, idx):
    print(graphql_data);
    acc = graphql_data.get("data", {}).get("account", {})
    if not acc:
        Logger.error(f"Tidak ada data akun ke-{idx+1} di response.")
        return config

    # Ambil semua mine_id (bisa lebih dari satu di masa depan)
    mine_ids = [m["id"] for m in acc.get("mines", []) if m.get("id")]
    # Ambil semua factory_id dari seluruh area di seluruh land plot
    factory_ids = []
    area_ids = []
    for land_plot in acc.get("landPlots", []):
        for area in land_plot.get("areas", []):
            if area.get("id"):
                area_ids.append(area["id"])
            for f in area.get("factories", []):
                fid = f.get("factory", {}).get("id")
                if fid:
                    factory_ids.append(fid)

    accno = idx+1
    config[f"mineIds_{accno}"] = mine_ids
    config[f"factoryIds_{accno}"] = factory_ids
    config[f"areaIds_{accno}"] = area_ids
    Logger.info(f"Config akun ke-{accno} diupdate dari data GraphQL.")
    return config

def upgrade_mine(token, mine_id):
    Logger.action(f"UPGRADE_MINE (ID: {mine_id})...")
    return post_action(token, "UPGRADE_MINE", {"mineId": mine_id})

def claim_mine(token, mine_id):
    Logger.action(f"CLAIM_MINE (ID: {mine_id})...")
    return post_action(token, "CLAIM_MINE", {"mineId": mine_id})

def start_mine(token, mine_id):
    Logger.action(f"START_MINE (ID: {mine_id})...")
    return post_action(token, "START_MINE", {"mineId": mine_id})

def upgrade_factory(token, factory_id):
    Logger.action(f"UPGRADE_FACTORY (ID: {factory_id})...")
    return post_action(token, "UPGRADE_FACTORY", {"factoryId": factory_id})

def start_factory(token, factory_id):
    Logger.action(f"START_FACTORY (ID: {factory_id})...")
    return post_action(token, "START_FACTORY", {"factoryId": factory_id})

def handle_claim_area(token, area_id, account, index):
    Logger.action(f"CLAIM_AREA (ID: {area_id})...")
    amount = 9999
    new_account = post_action(token, "CLAIM_AREA", {"areaId": area_id, "amountToClaim": amount})
    if new_account:
        Logger.info(f"CLAIM_AREA berhasil!")
        return new_account
    else:
        Logger.warn(f"CLAIM_AREA gagal.")
        return account


def show_menu():
    table = Table(title="📜 MENU FITUR BOT CRAFTWORLD", header_style="bold magenta")
    table.add_column("No", style="cyan", width=5)
    table.add_column("Fitur", style="green")
    table.add_column("Deskripsi", style="white")

    table.add_row("1", "CLAIM_AREA", "Mengklaim semua area di land plot")
    table.add_row("2", "START_FACTORY", "Menyalakan semua factory yang tersedia")
    table.add_row("3", "UPGRADE_FACTORY", "Meningkatkan level semua factory")
    table.add_row("4", "CLAIM_MINE", "Mengambil resource dari semua mine")
    table.add_row("5", "UPGRADE_MINE", "Meningkatkan level semua mine")
    table.add_row("6", "START_MINE", "Menyalakan semua mine")

    console.print(table)

def main():
    Logger.watermark()
    show_menu()
    while True:
        Logger.step("🔄 Mulai sync & update config otomatis dari GraphQL...")

        config = read_config()
        if not config:
            Logger.error("Config tidak ditemukan.")
            return

        account_count = len([k for k in config if k.startswith('apiKey_')])
        if account_count == 0:
            Logger.error("Tidak ada akun di config.")
            return

        for idx in range(account_count):
            api_key = config.get(f"apiKey_{idx+1}")
            refresh_token = config.get(f"refresh_token_{idx+1}")
            if not api_key or not refresh_token:
                Logger.error(f"API key/refresh_token untuk akun ke-{idx+1} tidak ditemukan.")
                continue

            token = get_account_token(idx, api_key, refresh_token)
            if not token:
                Logger.error(f"Gagal dapat token untuk akun ke-{idx+1}.")
                continue

            graphql_data = fetch_graphql_data(token)
            if graphql_data:
                config = extract_and_update_config(graphql_data, config, idx)

            # --- Ambil semua id dari config hasil GraphQL sync ---
            mine_ids = config.get(f"mineIds_{idx+1}", [])
            factory_ids = config.get(f"factoryIds_{idx+1}", [])
            area_ids = config.get(f"areaIds_{idx+1}", [])

            # Claim semua area
            dummy_account = {} # tidak penting di mode loop bulk
            for area_id in area_ids:
                handle_claim_area(token, area_id, dummy_account, idx)

            # Start semua factory
            for factory_id in factory_ids:
                start_factory(token, factory_id)

            # Upgrade semua mine
            for mine_id in mine_ids:
                claim_mine(token, mine_id)
                upgrade_mine(token, mine_id)
                start_mine(token, mine_id)

            # Upgrade semua factory
            for factory_id in factory_ids:
                upgrade_factory(token, factory_id)

        # Save config (update otomatis dari GraphQL)
        # with open('config.json', 'w') as f:
        #     json.dump(config, f, indent=4)
        Logger.info("Config.json berhasil diupdate otomatis untuk semua akun.")
        Logger.step("⏳ Menunggu 30 detik sebelum sync berikutnya...\n")
        time.sleep(30)

if __name__ == "__main__":
    main()
