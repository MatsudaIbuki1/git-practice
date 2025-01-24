import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

# SQLiteデータベースの設定
DB_PATH = "tour_data.db"

def initialize_db():
    """データベースを初期化する関数"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tour_name TEXT,
            price INTEGER,
            season TEXT,
            region TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def scrape_tour_data(base_url, region, season):
    """
    ツアーデータをスクレイピングする関数
    - base_url: https://www.jalan.net
    - region: 地域名（例: 北海道, 東北）
    - season: 季節名（例: 冬, 春）
    """
    url = f"{base_url}/{region}/{season}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # 仮のスクレイピング構造
    tours = []
    for tour in soup.find_all("div", class_="tour-item"):
        name = tour.find("h2").get_text(strip=True)
        price = int(tour.find("span", class_="price").get_text(strip=True).replace("¥", "").replace(",", ""))
        tours.append((name, price, season, region))
    return tours

def save_to_db(data):
    """スクレイピングしたデータをSQLiteに保存する関数"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO tours (tour_name, price, season, region)
        VALUES (?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

def analyze_tour_data():
    """データベースからデータを集計する関数"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT season, COUNT(*) AS tour_count
        FROM tours
        GROUP BY season
    """)
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    # データベース初期化
    initialize_db()

    # スクレイピングの実行（例としてURLや地域・季節を仮置き）
    BASE_URL = "https://example.com/tours"  # 本番では「じゃらん」のURLを指定
    regions = ["hokkaido", "tohoku", "chubu"]
    seasons = ["winter", "spring"]

    for region in regions:
        for season in seasons:
            print(f"Scraping {region} - {season}")
            data = scrape_tour_data(BASE_URL, region, season)
            save_to_db(data)

    # 集計結果を出力
    print("Seasonal Tour Counts:")
    for season, count in analyze_tour_data():
        print(f"{season}: {count} tours")
