import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def scrape_judulseries(url):
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request gagal: {e}")
        return

    if response.status_code != 200:
        print(f"[ERROR] Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'lxml')

    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.text.strip()
        valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        safe_title = ''.join(c for c in title if c in valid_chars).replace(' ', '_')
    else:
        safe_title = "output"

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "komiku_title_list")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"{safe_title}.txt")
    judulseries_elements = soup.find_all('td', class_='judulseries')

    urls = []
    for elem in judulseries_elements:
        link_tag = elem.find('a')
        if link_tag and 'href' in link_tag.attrs:
            full_url = urljoin(url, link_tag['href'])
            urls.append(full_url)

    urls.reverse()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(urls))

    print(f"[DONE] {len(urls)} URL disimpan ke: {output_file}")


if __name__ == "__main__":
    target_url = input("Masukkan URL komiku: ").strip()
    scrape_judulseries(target_url)
