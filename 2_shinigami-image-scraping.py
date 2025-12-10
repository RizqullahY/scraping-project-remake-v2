import os
import time
import shutil
import requests
from InquirerPy import inquirer
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTER_LIST_DIR = os.path.join(BASE_DIR, "shinigami_chapter_list")
RESULT_DIR = os.path.join(BASE_DIR, "shinigami_result")

os.makedirs(CHAPTER_LIST_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# ======================================================
# DOWNLOAD IMAGE (WITH RETRY)
# ======================================================
def download_image(url, path, retries=4):
    for attempt in range(retries):
        try:
            with requests.get(url, stream=True, timeout=10) as r:
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
                    print(f"[OK] {os.path.basename(path)}")
                    return True
        except RequestException:
            pass

        print(f"[Retry {attempt+1}/{retries}] {url}")

    print(f"[FAILED] {url}")
    return False


# ======================================================
# SCRAPE 1 CHAPTER - MULTI THREAD
# ======================================================
def scrape_chapter(uuid, output_dir):
    api_url = f"https://api.shngm.io/v1/chapter/detail/{uuid}"

    try:
        r = requests.get(api_url, timeout=10)
        data = r.json()["data"]
    except:
        print("[ERROR] API gagal.")
        return

    base = data["base_url"]
    path = data["chapter"]["path"]
    images = data["chapter"]["data"]

    total_images = len(images)
    padding = len(str(total_images))  # dynamic padding (3/4/5 digits)

    os.makedirs(output_dir, exist_ok=True)
    print(f"\nChapter {uuid} → {total_images} gambar (multi-thread download)")

    # MULTITHREADING
    futures = []
    with ThreadPoolExecutor(max_workers=12) as executor:

        for idx, img in enumerate(images, 1):
            img_url = base + path + img
            filename = f"{str(idx).zfill(padding)}.jpg"
            img_path = os.path.join(output_dir, filename)

            futures.append(
                executor.submit(download_image, img_url, img_path)
            )

        for _ in as_completed(futures):
            pass  # hanya menunggu sampai selesai

    print(f"[DONE] Chapter selesai: {output_dir}")


# ======================================================
# PICK TITLE FILE
# ======================================================
def pick_file():
    files = [f for f in os.listdir(CHAPTER_LIST_DIR) if f.endswith(".txt")]

    if not files:
        print("Tidak ada file txt di folder.")
        return None, None

    choice = inquirer.select(
        message="Pilih manga:",
        choices=files,
        default=files[0]
    ).execute()

    return os.path.join(CHAPTER_LIST_DIR, choice), choice


# ======================================================
# MAIN
# ======================================================
def main():
    print("=== SHINIGAMI IMAGE SCRAPER (MULTI WORKER) ===\n")

    txt_path, txt_name = pick_file()
    if txt_path is None:
        return

    title_folder = txt_name.replace(".txt", "")
    output_dir = os.path.join(RESULT_DIR, title_folder)
    os.makedirs(output_dir, exist_ok=True)

    # load urls
    with open(txt_path, "r", encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()]

    print(f"Total chapter: {len(urls)}")

    start = int(input("Mulai chapter: ")) - 1
    end = int(input("Akhir chapter: "))
    selected = urls[start:end]

    print(f"\nMulai scrape {len(selected)} chapter...\n")

    for idx, chapter_url in enumerate(selected, start=start + 1):
        uuid = chapter_url.rstrip("/").split("/")[-1]
        chap_folder = os.path.join(output_dir, f"chapter_{idx}")
        scrape_chapter(uuid, chap_folder)

    print("\n=== SELESAI ===")


if __name__ == "__main__":
    main()
