import json
import uuid
import requests
import time
import random
import threading
from rich.console import Console
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
        "content-type": "application/x-www-form-urlencoded"
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
    acc = graphql_data.get("data", {}).get("account", {})
    if not acc:
        Logger.error(f"Tidak ada data akun ke-{idx+1} di response.")
        return config

    mine_ids = [m["id"] for m in acc.get("mines", []) if m.get("id")]
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

def handle_claim_area(token, area_id):
    Logger.action(f"CLAIM_AREA (ID: {area_id})...")
    amount = 9999
    new_account = post_action(token, "CLAIM_AREA", {"areaId": area_id, "amountToClaim": amount})
    if new_account:
        Logger.info(f"CLAIM_AREA berhasil!")
    else:
        Logger.warn(f"CLAIM_AREA gagal.")

def run_account_loop(idx, api_key, refresh_token, config):
    while True:
        Logger.step(f"⏳ Mulai sync akun ke-{idx+1}...")
        token = get_account_token(idx, api_key, refresh_token)
        if not token:
            Logger.error(f"Token akun ke-{idx+1} gagal.")
            time.sleep(10)
            continue

        graphql_data = fetch_graphql_data(token)
        if graphql_data:
            config = extract_and_update_config(graphql_data, config, idx)

        mine_ids = config.get(f"mineIds_{idx+1}", [])
        factory_ids = config.get(f"factoryIds_{idx+1}", [])
        area_ids = config.get(f"areaIds_{idx+1}", [])

        for area_id in area_ids:
            handle_claim_area(token, area_id)

        for factory_id in factory_ids:
            start_factory(token, factory_id)

        for mine_id in mine_ids:
            claim_mine(token, mine_id)
            upgrade_mine(token, mine_id)
            start_mine(token, mine_id)

        for factory_id in factory_ids:
            upgrade_factory(token, factory_id)

        delay = random.randint(60, 140)
        Logger.step(f"✅ Akun ke-{idx+1} selesai. Menunggu {delay//60} menit...\n")
        time.sleep(delay)

def main():
    config = read_config()
    if not config:
        Logger.error("Gagal baca config.json.")
        return

    account_count = len([k for k in config if k.startswith("apiKey_")])
    if account_count == 0:
        Logger.error("Tidak ada akun ditemukan.")
        return

    Logger.watermark()
    for idx in range(account_count):
        api_key = config.get(f"apiKey_{idx+1}")
        refresh_token = config.get(f"refresh_token_{idx+1}")
        if not api_key or not refresh_token:
            Logger.error(f"Akun ke-{idx+1} tidak lengkap.")
            continue
        threading.Thread(target=run_account_loop, args=(idx, api_key, refresh_token, config), daemon=True).start()

    while True:
        time.sleep(999)

if __name__ == "__main__":
    main()
