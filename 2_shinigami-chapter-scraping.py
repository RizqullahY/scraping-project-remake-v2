import os
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TITLE_LIST_DIR = os.path.join(BASE_DIR, "shinigami_chapter_list")
os.makedirs(TITLE_LIST_DIR, exist_ok=True)

# =================================================================
# Extract UUID from Shinigami URL
# =================================================================
def extract_uuid(shinigami_url):
    return shinigami_url.rstrip("/").split("/")[-1]


# =================================================================
# Fetch ALL chapters with auto-pagination
# =================================================================
def fetch_all_chapters(uuid):
    page = 1
    page_size = 24
    all_items = []

    print("[INFO] Mengambil semua chapter...")

    while True:
        api_url = (
            f"https://api.shngm.io/v1/chapter/{uuid}/list"
            f"?page={page}&page_size={page_size}&sort_by=chapter_number&sort_order=asc"
        )

        r = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)

        if r.status_code != 200:
            print(f"[ERROR] API gagal diakses pada page {page}: {r.status_code}")
            break

        data = r.json()
        items = data.get("data", [])

        print(f"  - Page {page} | Items: {len(items)}")

        if not items:
            break  # tidak ada data → selesai

        all_items.extend(items)

        # Jika jumlah kurang dari page_size → ini page terakhir
        if len(items) < page_size:
            break

        page += 1

    print(f"[INFO] Total chapter terkumpul: {len(all_items)}")
    return all_items


# =================================================================
# Fetch manga title from detail API
# =================================================================
def fetch_manga_title(uuid):
    url = f"https://api.shngm.io/v1/manga/detail/{uuid}"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)

    if r.status_code != 200:
        print("[WARNING] Tidak bisa ambil title, pakai UUID saja.")
        return uuid

    data = r.json()
    return data.get("data", {}).get("title", uuid)


# =================================================================
# Convert JSON → chapter URLs
# =================================================================
def convert_to_chapter_urls(items):
    chapter_urls = []
    base_view = "https://08.shinigami.asia/chapter/"

    for chapter in items:
        chap_id = chapter.get("chapter_id")   # ← FIX DI SINI
        if chap_id:
            chapter_urls.append(base_view + chap_id)

    return chapter_urls


# =================================================================
# Save into TXT
# =================================================================
def save_to_txt(title, chapter_urls):
    safe_title = title.replace(" ", "_").replace("/", "_")
    output_path = os.path.join(TITLE_LIST_DIR, f"{safe_title}.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        for url in chapter_urls:
            f.write(url + "\n")

    print(f"[DONE] {len(chapter_urls)} chapter URL disimpan → {output_path}")


# =================================================================
# MAIN
# =================================================================
def main():
    print("=== SHINIGAMI TITLE SCRAPER (AUTO PAGE) ===")

    shini_url = input("Masukkan URL series shinigami: ").strip()
    uuid = extract_uuid(shini_url)

    # ambil seluruh chapter
    items = fetch_all_chapters(uuid)

    # ambil judul manga
    title = fetch_manga_title(uuid)
    print(f"[INFO] Manga Title: {title}")

    # ubah JSON → URL
    chapter_urls = convert_to_chapter_urls(items)

    # simpan ke TXT
    save_to_txt(title, chapter_urls)


if __name__ == "__main__":
    main()
