import pandas as pd
from openpyxl import Workbook
import os
from datetime import datetime

def read_ip_from_excel(file_path):
    """ 讀取 Excel 檔案，取得 IP 列表 """
    df = pd.read_excel(file_path)
    if "IP" not in df.columns:
        return None
    return df["IP"].dropna().astype(str).tolist()

def open_results_in_excel(results):
    """ 開啟 Excel，分類高風險 IP，但不存檔 """
    high_risk = []
    normal = []

    for result in results:
        # **使用 Risk Level 來分類高風險與一般 IP**
        if result.get("Risk Level", "低風險") == "高風險":
            high_risk.append(result)
        else:
            normal.append(result)

    wb = Workbook()

    # **高風險 IP**
    ws1 = wb.active
    ws1.title = "高風險 IP"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 取得當前時間
    ws1.append([f"查詢時間: {timestamp}"])  # 在第一行加入查詢時間
    if high_risk:
        ws1.append(list(high_risk[0].keys()))  # 加入標題行
        for row in high_risk:
            ws1.append(list(row.values()))
    else:
        ws1.append(["沒有高風險 IP"])

    # **一般 IP**
    ws2 = wb.create_sheet(title="一般 IP")
    ws2.append([f"查詢時間: {timestamp}"])  # 在第一行加入查詢時間
    if normal:
        ws2.append(list(normal[0].keys()))  # 加入標題行
        for row in normal:
            ws2.append(list(row.values()))
    else:
        ws2.append(["沒有一般 IP"])

    temp_file = "/tmp/ip_results.xlsx"
    wb.save(temp_file)
    os.system(f"open {temp_file}")