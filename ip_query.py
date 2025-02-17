import asyncio
import aiohttp
from ipwhois import IPWhois
from config import ABUSEIPDB_API_KEY

async def get_ip_info(session, ip):
    """ 查詢 IP 位置、ISP、ASN、VPN/代理/資料中心 """
    url = f"http://ip-api.com/json/{ip}?fields=status,message,country,isp,as,proxy,hosting"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return {
                "IP": ip,
                "Country": data.get("country", "N/A"),
                "ASN": data.get("as", "N/A"),
                "ISP": data.get("isp", "N/A"),
                "Proxy": "Yes" if data.get("proxy", False) else "No",
                "Hosting": "Yes" if data.get("hosting", False) else "No",
            }
    return {"IP": ip, "Country": "Error", "ASN": "Error", "ISP": "Error", "Proxy": "Error", "Hosting": "Error"}

async def check_blacklist(session, ip):
    """ 查詢 AbuseIPDB 黑名單分數 """
    url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}&maxAgeInDays=90"
    headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return {
                "IP": ip,
                "Blacklist_Score": data["data"].get("abuseConfidenceScore", 0)
            }
    return {"IP": ip, "Blacklist_Score": 0}

def get_whois_info(ip):
    """ 查詢 WHOIS 訊息，獲取 IP 申請者名稱 """
    try:
        obj = IPWhois(ip)
        result = obj.lookup_rdap()
        return result.get("network", {}).get("name", "N/A")
    except:
        return "N/A"

async def batch_query(ip_list):
    async with aiohttp.ClientSession() as session:
        # **同時查詢 IP 位置 & 黑名單**
        tasks = [get_ip_info(session, ip) for ip in ip_list]
        blacklist_tasks = [check_blacklist(session, ip) for ip in ip_list]

        ip_results, blacklist_results = await asyncio.gather(
            asyncio.gather(*tasks),
            asyncio.gather(*blacklist_tasks)
        )

        # **整合資料**
        for i in range(len(ip_results)):
            ip_results[i]["Blacklist_Score"] = blacklist_results[i]["Blacklist_Score"]
            ip_results[i]["Whois Name"] = get_whois_info(ip_results[i]["IP"])

            # **提高風險級別**
            risk_level = "低風險"
            if ip_results[i]["Blacklist_Score"] > 50:
                risk_level = "高風險"
            if ip_results[i]["Proxy"] == "Yes" or ip_results[i]["Hosting"] == "Yes":
                risk_level = "高風險"

            ip_results[i]["Risk Level"] = risk_level  # 新增風險等級欄位

        return ip_results