import requests
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

BV_LIST = [
    "BV1PQFQzzEfU",
    "BV1JwauzREYL",
    "BV1gGsLeEEz1",
    "BV1ZX4y1x7pG",
    "BV1hA411k7Rd"
]

# ======================
# 获取播放量
# ======================
def get_view(bvid):
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    r = requests.get(url, timeout=10).json()
    return r["data"]["stat"]["view"]

# ======================
# 记录数据 + 时增
# ======================
def record():
    os.makedirs("data", exist_ok=True)
    file = "data/data.csv"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    old = {}
    if os.path.exists(file):
        df_old = pd.read_csv(file)
        for b in BV_LIST:
            temp = df_old[df_old["bvid"] == b]
            if not temp.empty:
                old[b] = temp.iloc[-1]["view"]

    new_file = not os.path.exists(file)

    with open(file, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        if new_file:
            w.writerow(["time", "bvid", "view", "hour_change"])

        for bvid in BV_LIST:
            try:
                view = get_view(bvid)

                hour_change = view - old[bvid] if bvid in old else 0

                w.writerow([now, bvid, view, hour_change])

                print(bvid, view, hour_change)

            except:
                pass

# ======================
# 导出 Excel + 长图
# ======================
def export():
    file = "data/data.csv"
    if not os.path.exists(file):
        return

    df = pd.read_csv(file)

    today = datetime.now().strftime("%Y-%m-%d")
    df = df[df["time"].str.contains(today)]

    if df.empty:
        return

    os.makedirs("data", exist_ok=True)

    result = []

    for bvid in df["bvid"].unique():
        temp = df[df["bvid"] == bvid]

        if len(temp) < 2:
            continue

        start = temp.iloc[0]["view"]
        end = temp.iloc[-1]["view"]

        total = end - start
        hour_last = temp.iloc[-1]["hour_change"]

        result.append([bvid, start, end, total, hour_last])

    pd.DataFrame(result, columns=["BV","开始","结束","日增","时增"]).to_excel(
        "data/report.xlsx", index=False
    )

    # 粉色长图
    plt.figure(figsize=(10,6))

    for bvid in df["bvid"].unique():
        temp = df[df["bvid"] == bvid]
        plt.plot(temp["view"].values, label=bvid)

    plt.title("💗 B站数据日报 💗")
    plt.legend()
    plt.tight_layout()
    plt.savefig("data/report.png", dpi=200)

# ======================
# 执行入口
# ======================
if __name__ == "__star__":
    record()
    export()
