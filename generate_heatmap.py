import os
from notion_client import Client
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 初始化 Notion 客户端
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=NOTION_API_KEY)

def fetch_notion_data():
    """从 Notion 数据库中获取数据"""
    results = []
    has_more = True
    next_cursor = None

    while has_more:
        response = notion.databases.query(
            **{
                "database_id": DATABASE_ID,
                "start_cursor": next_cursor,
            }
        )
        results.extend(response["results"])
        has_more = response["has_more"]
        next_cursor = response.get("next_cursor")

    # 提取日期字段
    dates = []
    for item in results:
        properties = item.get("properties", {})
        date_property = properties.get("Date")  # 假设日期字段名为 "Date"
        if date_property and date_property["type"] == "date":
            date_value = date_property["date"].get("start")
            if date_value:
                dates.append(date_value)

    return dates

def generate_heatmap(dates):
    """根据日期生成热力图"""
    # 转换日期为 DataFrame
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    # 按月统计每日记录数
    heatmap_data = df.groupby(["month", "day"]).size().unstack(fill_value=0)

    # 生成热力图
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", linewidths=0.5, annot=False)
    plt.title("Diary Heatmap", fontsize=16)
    plt.xlabel("Day")
    plt.ylabel("Month")

    # 保存热力图
    output_path = "heatmap.svg"
    plt.savefig(output_path, format="svg")
    print(f"热力图已保存到 {output_path}")

if __name__ == "__main__":
    # 获取 Notion 数据
    dates = fetch_notion_data()

    # 生成热力图
    if dates:
        generate_heatmap(dates)
    else:
        print("未获取到任何日期数据！")