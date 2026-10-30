import csv
import time
from bs4 import BeautifulSoup
import requests

url = "https://www.musashino-u.ac.jp"

header = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

sitemap = {}
visited = set()
queue = [url]

# 事前にCSVを作成しヘッダーを書き込む
with open("sitemap.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["URL", "Title"])

print("スクレイピングを開始します...")

while queue:
    current_url = queue.pop(0)

    # #（アンカー）を削って重複を防止
    current_url = current_url.split("#")[0]

    if current_url in visited:
        continue

    visited.add(current_url)
    time.sleep(0.001)  # 負荷軽減のための1秒待機

    try:
        res = requests.get(current_url, headers=header)

        if res.status_code != 200 or "text/html" not in res.headers.get(
            "Content-Type", ""
        ):
            continue

        html_soup = BeautifulSoup(res.content, "html.parser")
        title_tag = html_soup.find("title")
        if title_tag and title_tag.string:
            title_text = title_tag.string.strip()
        else:
            title_text = "タイトルなし"

        # 辞書に格納
        sitemap[current_url] = title_text

        # リアルタイムでCSVに保存
        with open("sitemap.csv", "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([current_url, title_text])

        # 件数の進捗を表示
        print(f"[{len(sitemap)}件取得] {current_url} -> {title_text}")

        # 3000件に達したら自動で終了したい場合は以下のコメントを外す
        # if len(sitemap) >= 3000:
        #     print("3000件に達したため終了します。")
        #     break

        a_list = html_soup.find_all("a")

        for a in a_list:
            href = a.get("href")
            if not href:
                continue

            if href.startswith("http://") or href.startswith("https://"):
                full_url = href
            elif href.startswith("/"):
                full_url = url + href
            else:
                full_url = url + "/" + href

            # 追加するURLからも # 以降を削る
            full_url = full_url.split("#")[0]

            if ("musashino-u.ac.jp" in full_url) and (full_url not in visited):
                queue.append(full_url)

    except Exception as e:
        print(f"エラー発生 ({current_url}): {e}")

print(f"完了！{len(sitemap)}件のデータをsitemap.csvに保存しました。")