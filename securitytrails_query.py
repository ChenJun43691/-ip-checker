import aiohttp
from config import SECURITYTRAILS_API_KEY  # ✅ 從 `config.py` 讀取 API Key

BASE_URL = "https://api.securitytrails.com/v1/ips"

async def fetch_securitytrails_data(session, ip, endpoint):
    """ 通用函數，查詢 SecurityTrails API """
    url = f"{BASE_URL}/{ip}/{endpoint}"
    headers = {"APIKEY": SECURITYTRAILS_API_KEY}  # ✅ 使用 `config.py` 內的 API Key
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        return None

async def get_reverse_dns(session, ip):
    """ 查詢 IP 的反向 DNS """
    data = await fetch_securitytrails_data(session, ip, "dns")
    return {"IP": ip, "Reverse DNS": data.get("hostname", "N/A") if data else "Error"}

async def get_historical_dns(session, ip):
    """ 查詢 IP 的歷史 DNS 記錄 """
    data = await fetch_securitytrails_data(session, ip, "dns/history")
    return {"IP": ip, "Historical DNS": data.get("records", []) if data else "Error"}

async def get_ip_subnet(session, ip):
    """ 查詢 IP 所屬的子網段 """
    data = await fetch_securitytrails_data(session, ip, "subnet")
    return {"IP": ip, "Subnet": data.get("subnet", "N/A") if data else "Error"}

async def get_ip_whois(session, ip):
    """ 查詢 IP WHOIS 訊息 """
    data = await fetch_securitytrails_data(session, ip, "whois")
    return {"IP": ip, "WHOIS Owner": data.get("owner", "N/A") if data else "Error"}

async def get_ip_tags(session, ip):
    """ 查詢 IP 的標籤（是否屬於雲端服務） """
    data = await fetch_securitytrails_data(session, ip, "tags")
    return {"IP": ip, "Tags": data.get("tags", []) if data else "Error"}