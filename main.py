import tkinter as tk
from PIL import Image, ImageTk  # 需要安裝 Pillow 套件
from tkinter import filedialog, messagebox, ttk
import asyncio
import os  # 新增 os 模組來檢查圖示是否存在
from ip_query import batch_query
from file_handler import read_ip_from_excel, open_results_in_excel
from utils import get_random_quote

# **初始化 Tkinter UI**
root = tk.Tk()
root.title("詐欺獵人 IP 查詢工具")
root.geometry("600x450")  # 增加 UI 高度，避免內容過於擁擠

# **載入圖示**
icon_path = "pollogo.icns"
if os.path.exists(icon_path):
    try:
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        root.iconphoto(False, icon_photo)
    except Exception as e:
        print(f"⚠️ 載入圖示失敗: {e}")
else:
    print("⚠️ 圖示文件不存在，將不載入自訂圖示")

# **變數設定**
file_path = tk.StringVar()
progress_label = tk.StringVar(value="等待查詢...")
progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
start_button = None

# **選擇 Excel 檔案**
def select_file():
    filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if filename:
        file_path.set(filename)

# **執行 IP 查詢**
def run_query():
    global start_button

    if not file_path.get():
        messagebox.showerror("錯誤", "請先選擇 Excel 檔案！")
        return

    ip_list = read_ip_from_excel(file_path.get())  
    if not ip_list:
        messagebox.showerror("錯誤", "Excel 必須包含 'IP' 欄位！")
        return

    progress_label.set("查詢中...")
    progress_bar["value"] = 0
    progress_bar["maximum"] = len(ip_list)
    root.update()

    start_button.config(state=tk.DISABLED)

    async def async_run():
        results = []
        total_ips = len(ip_list)

        for i, ip in enumerate(ip_list):
            result = await batch_query([ip])
            results.append(result[0])

            progress_label.set(f"查詢進度: {i+1}/{total_ips}")
            progress_bar["value"] = i+1
            root.update()

        open_results_in_excel(results)

        progress_label.set("查詢完成！")
        messagebox.showinfo("完成", "查詢結果已顯示")

        start_button.config(state=tk.NORMAL)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_run())

# **建立 UI 介面**
tk.Label(root, text="IP 批量查詢工具", font=("Arial", 16)).pack(pady=10)
tk.Button(root, text="選擇 Excel 檔案", command=select_file).pack()
tk.Label(root, textvariable=file_path, fg="blue").pack(pady=5)

start_button = tk.Button(root, text="開始查詢", command=run_query)
start_button.pack(pady=10)

progress_bar.pack(pady=5)
tk.Label(root, textvariable=progress_label, fg="red").pack(pady=5)

tk.Label(root, text=get_random_quote(), fg="gray", font=("Arial", 10)).pack(pady=10)

# **About Me（放在 UI 最下方）**
about_text = """🚔 IP 批量查詢工具 功能說明 🚔  
開發者：高雄市刑大
🎯 用途：快速查詢可疑 IP，判斷是否為 VPN / 代理 / 黑名單  
🔎 功能：
   ✅ 批量 IP 查詢  
   ✅ VPN / 代理 / 資料中心 判定  
   ✅ 黑名單評分 (AbuseIPDB)  
   ✅ WHOIS 資訊  

📌 建議 & 反饋：來信“e43691@kcg.gov.tw”(來信註明單位、姓名、公務電話)
"""

about_label = tk.Label(root, text=about_text, fg="gray", font=("Arial", 10), justify="left", anchor="w")
about_label.pack(pady=10, padx=20, fill="x")  # 讓 About Me 內容橫向填滿 UI 底部

# **啟動 UI**
root.mainloop()