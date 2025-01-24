import requests
import sqlite3
from datetime import datetime
import flet as ft

# 気象庁APIエンドポイント
AREA_API_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_API_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

# SQLiteデータベースの初期化
def init_db():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    # エリア情報テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Area (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        code TEXT UNIQUE
    )
    """)

    # 天気情報テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area_code TEXT,
        date TEXT,
        weather TEXT,
        temperature TEXT,
        created_at TEXT,
        FOREIGN KEY (area_code) REFERENCES Area (code)
    )
    """)
    conn.commit()
    conn.close()

# エリア情報をDBに保存
def save_area_data(area_data):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    for region_name, region_info in area_data["offices"].items():
        cursor.execute("""
        INSERT OR IGNORE INTO Area (name, code) VALUES (?, ?)
        """, (region_name, region_info["parent"]))
    conn.commit()
    conn.close()

# 天気情報をDBに保存
def save_weather_data(area_code, weather_data):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for forecast in weather_data[0]["timeSeries"][0]["areas"]:
        weather_text = forecast["weathers"][0]
        temperature = ", ".join(forecast.get("temps", ["-"]))
        cursor.execute("""
        INSERT INTO Weather (area_code, date, weather, temperature, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (area_code, weather_data[0]["reportDatetime"], weather_text, temperature, now))
    conn.commit()
    conn.close()

# DBからエリア情報を取得
def get_area_list():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, code FROM Area")
    rows = cursor.fetchall()
    conn.close()
    return rows

# DBから天気情報を取得
def get_weather_data(area_code):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT date, weather, temperature FROM Weather WHERE area_code = ?
    """, (area_code,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# 気象庁APIからエリアリストを取得
def fetch_area_list():
    response = requests.get(AREA_API_URL)
    return response.json()

# 気象庁APIから天気予報を取得
def fetch_weather_forecast(area_code):
    url = FORECAST_API_URL_TEMPLATE.format(area_code=area_code)
    response = requests.get(url)
    return response.json()

# メインアプリケーション
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.scroll = "adaptive"

    # DB初期化
    init_db()

    # エリアデータ取得と保存
    area_data = fetch_area_list()
    save_area_data(area_data)

    # 初期状態
    selected_area_code = None
    content = ft.Column()

    # 地域選択のリストを作成
    def create_area_list_view():
        areas = get_area_list()
        tiles = []
        for name, code in areas:
            tile = ft.ListTile(
                title=ft.Text(name),
                on_click=lambda e, code=code: display_weather(code),
            )
            tiles.append(tile)
        return tiles

    # 天気予報を表示
    def display_weather(area_code):
        nonlocal selected_area_code
        selected_area_code = area_code
        content.controls.clear()
        content.controls.append(
            ft.Text(f"地域コード: {area_code} の天気予報", size=20, weight="bold")
        )

        # DBから天気データを取得
        weather_data = get_weather_data(area_code)
        if not weather_data:
            # 天気データがない場合はAPIから取得
            api_weather_data = fetch_weather_forecast(area_code)
            save_weather_data(area_code, api_weather_data)
            weather_data = get_weather_data(area_code)

        for date, weather, temperature in weather_data:
            content.controls.append(
                ft.ExpansionTile(
                    title=ft.Text(f"{date}: {weather}"),
                    children=[ft.Text(f"気温: {temperature}")]
                )
            )
        page.update()

    # 初期表示（地域リスト）
    content.controls.extend(create_area_list_view())

    # レイアウトを作成
    page.add(
        ft.Row(
            [
                ft.Container(content=content, expand=True),
            ],
            expand=True,
        )
    )

ft.app(target=main)
