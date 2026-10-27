import requests
from bs4 import BeautifulSoup
import time
import csv

url = 'https://www.musashino-u.ac.jp'

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

sitemap = {}

visited = set()
queue = [url]

with open("sitemap.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["URL", "Title"])

while queue:
    current_url = queue.pop(0)
    if current_url in visited:
        continue
    visited.add(current_url)
    time.sleep(1)

    try:
        res = requests.get(current_url, headers=header)

        if res.status_code != 200 or "text/html" not in res.headers.get("Content-Type", ""):
            continue

        html_soup = BeautifulSoup(res.content, "html.parser")
        title_tag = html_soup.find("title")
        if title_tag and title_tag.string:
            title_text = title_tag.string.strip()
        else:
            title_text = "タイトルなし"

        sitemap[current_url] = title_text
        print(f"取得成功: {current_url} -> {title_text}")

        with open("sitemap.csv", "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([current_url, title_text])

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

            if ("musashino-u.ac.jp" in full_url) and (full_url not in visited):
                queue.append(full_url)

    except Exception as e:
        print(f"エラー発生 ({current_url}): {e}")

print(f"完了！{len(sitemap)}件のデータをsitemap.csvに保存しました。")
