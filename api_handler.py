import aiohttp
from config import SECURITYTRAILS_API_KEY, ABUSEIPDB_API_KEY  #  只保留這兩個 API Key

# SecurityTrails API
SECURITYTRAILS_URL = "https://api.securitytrails.com/v1"
# AbuseIPDB API
ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"

async def fetch_json(session, url, headers=None, params=None):
    """ 通用 API 請求函數 """
    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            return await response.json()
        return None

async def get_domain_info(session, domain):
    """ 查詢 SecurityTrails 網域資訊 """
    url = f"{SECURITYTRAILS_URL}/domain/{domain}"
    headers = {"APIKEY": SECURITYTRAILS_API_KEY}
    return await fetch_json(session, url, headers)

async def get_domain_whois(session, domain):
    """ 查詢 SecurityTrails 網域 WHOIS 記錄 """
    url = f"{SECURITYTRAILS_URL}/domain/{domain}/whois"
    headers = {"APIKEY": SECURITYTRAILS_API_KEY}
    return await fetch_json(session, url, headers)

async def get_domain_dns_history(session, domain):
    """ 查詢 SecurityTrails 網域歷史 DNS 記錄 """
    url = f"{SECURITYTRAILS_URL}/history/{domain}/dns"
    headers = {"APIKEY": SECURITYTRAILS_API_KEY}
    return await fetch_json(session, url, headers)

async def get_abuseipdb_report(session, ip):
    """ 查詢 AbuseIPDB，檢查 IP 是否被舉報為惡意活動 """
    params = {"ipAddress": ip, "maxAgeInDays": 90}
    headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
    data = await fetch_json(session, ABUSEIPDB_URL, headers, params)

    if data:
        return {
            "IP": ip,
            "Abuse Score": data.get("data", {}).get("abuseConfidenceScore", "N/A"),
            "Last Reported": data.get("data", {}).get("lastReportedAt", "N/A"),
            "Reports": data.get("data", {}).get("totalReports", 0),
        }
    return {"IP": ip, "Abuse Score": "Error", "Last Reported": "Error", "Reports": "Error"}
