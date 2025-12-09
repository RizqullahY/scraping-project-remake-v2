import os
import time
import requests
import shutil
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from InquirerPy import inquirer
from requests.exceptions import RequestException
from utils import generate_index_from_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTER_LIST_DIR = os.path.join(BASE_DIR, "komiku_chapter_list")
RESULT_DIR = os.path.join(BASE_DIR, "komiku_result")

os.makedirs(CHAPTER_LIST_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

def download_image(img_url, img_path, retries=5):
    for attempt in range(retries):
        try:
            with requests.get(
                img_url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10,
                stream=True
            ) as r:

                if r.status_code == 200:
                    with open(img_path, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
                    print(f"[OK] {os.path.basename(img_path)}")
                    return

        except RequestException:
            pass

        print(f"[Retry {attempt+1}/{retries}] {img_url}")
        time.sleep(1)

    print(f"[FAILED] {img_url}")


# ======================================================
# SCRAPE 1 CHAPTER (MULTITHREADED)
# ======================================================
def scrape_images_from_url(url, output_folder, workers=20):
    print(f"\n[SCRAPING] {url}")

    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
    except RequestException:
        print("[ERROR] Gagal fetch halaman.")
        return

    if r.status_code != 200:
        print(f"[ERROR] Status code: {r.status_code}")
        return

    soup = BeautifulSoup(r.text, "lxml")
    images = soup.find_all("img", itemprop="image")
    image_urls = [img["src"] for img in images if "src" in img.attrs]

    if not image_urls:
        print("[WARNING] Tidak ada gambar ditemukan.")
        return

    os.makedirs(output_folder, exist_ok=True)

    print(f"Found {len(image_urls)} images (multithread {workers} workers)")

    # MULTITHREAD DOWNLOAD
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []

        for i, img_url in enumerate(image_urls, 1):
            img_path = os.path.join(output_folder, f"image_{i}.jpg")
            futures.append(
                executor.submit(download_image, img_url, img_path)
            )

        for _ in as_completed(futures):
            pass

    print(f"[DONE] Chapter complete: {output_folder}")


# ======================================================
# SELECT TITLE FILE
# ======================================================
def pick_title_file():
    txt_files = [f for f in os.listdir(CHAPTER_LIST_DIR) if f.endswith(".txt")]

    if not txt_files:
        print("Tidak ada file .txt di title_list/")
        return None

    choice = inquirer.select(
        message="Pilih title yang akan di-scrape:",
        choices=txt_files,
        default=txt_files[0]
    ).execute()

    return os.path.join(CHAPTER_LIST_DIR, choice), choice


# ======================================================
# MAIN PROCESS
# ======================================================
def main():
    print("=== Komik Scraper CLI ===\n")

    txt_path, txt_name = pick_title_file()
    if not txt_path:
        return

    title_folder = txt_name.replace(".txt", "")
    output_dir = os.path.join(RESULT_DIR, title_folder)
    os.makedirs(output_dir, exist_ok=True)

    # Baca daftar link
    with open(txt_path, "r", encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()]

    print(f"\nTotal chapter tersedia: {len(urls)}\n")

    # RANGE INPUT
    start = int(input("Chapter mulai (angka): ")) - 1
    end = int(input("Chapter akhir (angka): "))
    selected = urls[start:end]

    print(f"\nMemproses {len(selected)} chapter...\n")

    # LOOP SCRAPE CHAPTER
    for idx, chapter_url in enumerate(selected, start=start + 1):
        chapter_folder = os.path.join(output_dir, f"chapter_{idx}")
        scrape_images_from_url(chapter_url, chapter_folder)
        # generate_index_from_template(chapter_folder)

    print("\n[Selesai] Semua chapter selesai discrape!")
    print(f"Hasil disimpan di: {output_dir}")
    


if __name__ == "__main__":
    main()