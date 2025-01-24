import requests
import flet as ft


# 気象庁APIエンドポイント
AREA_API_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_API_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"


def fetch_area_list():
    """地域リストを取得"""
    response = requests.get(AREA_API_URL)
    return response.json()


def fetch_weather_forecast(area_code):
    """指定された地域の天気予報を取得"""
    url = FORECAST_API_URL_TEMPLATE.format(area_code=area_code)
    response = requests.get(url)
    return response.json()


def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.scroll = "adaptive"

    # 初期状態
    area_data = fetch_area_list()
    selected_area_code = None

    # UI要素
    rail = ft.NavigationRail(
        selected_index=0,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.WB_SUNNY, label="地域選択"),
        ],
        label_type="all",
    )

    content = ft.Column()

    # 地域選択のリストを作成
    def create_area_list_view():
        regions = area_data["offices"]
        tiles = []
        for region_name, region_info in regions.items():
            # 地域ごとにリストタイルを作成
            tile = ft.ListTile(
                title=ft.Text(region_name),
                on_click=lambda e, code=region_info["parent"]: display_weather(code),
            )
            tiles.append(tile)
        return tiles

    # 天気予報を表示
    def display_weather(area_code):
        content.controls.clear()
        weather_data = fetch_weather_forecast(area_code)
        content.controls.append(
            ft.Text(f"地域コード: {area_code} の天気予報", size=20, weight="bold")
        )
        # 天気予報を表示する部分
        for forecast in weather_data[0]["timeSeries"][0]["areas"]:
            weather_text = forecast["weathers"][0]
            weather_tile = ft.ExpansionTile(
                title=ft.Text(f"天気: {weather_text}"),
                children=[
                    ft.Text(f"天気詳細: {forecast['weathers'][0]}"),
                    ft.Text(f"気温: {forecast.get('temps', ['-'])[0]}"),
                ],
            )
            content.controls.append(weather_tile)
        page.update()

    # 初期表示（地域リスト）
    content.controls.extend(create_area_list_view())

    # レイアウトを作成
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Container(content=content, expand=True),
            ],
            expand=True,
        )
    )


ft.app(target=main)
