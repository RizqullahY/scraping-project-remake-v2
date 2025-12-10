import os
import re
import zipfile
from pathlib import Path
from InquirerPy import inquirer


# -----------------------------------------------------------
# UTIL: Parse input "1,2,5,10-15"
# -----------------------------------------------------------
def parse_selection(selection):
    numbers = set()
    parts = selection.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            numbers.update(range(start, end + 1))
        else:
            numbers.add(int(part))
    return sorted(numbers)


# -----------------------------------------------------------
# UTIL: Collect chapterXXX folders
# -----------------------------------------------------------
def collect_chapters(series_dir):
    chapters = {}
    for folder in series_dir.iterdir():
        if folder.is_dir() and folder.name.lower().startswith("chapter"):
            match = re.search(r"(\d+)", folder.name)
            if match:
                chapters[int(match.group(1))] = folder
    return dict(sorted(chapters.items()))


# -----------------------------------------------------------
# UTIL: Create ZIP for a batch of chapters
# -----------------------------------------------------------
def zip_batch(series_dir, chapters, start_num, end_num):
    prefix = series_dir.name
    zip_name = f"{prefix}_{start_num}-{end_num}.zip"
    zip_path = series_dir / zip_name

    # Wrapper folder = nama folder awal + _start-end
    wrapper_folder = f"{prefix}_{start_num}-{end_num}"

    print(f"\n📦 Membuat ZIP: {zip_name}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for num in range(start_num, end_num + 1):
            if num not in chapters:
                continue
            
            chapter_folder = chapters[num]

            for file_path in chapter_folder.rglob("*"):
                if file_path.is_file():
                    arcname = Path(wrapper_folder) / file_path.relative_to(series_dir)
                    zf.write(file_path, arcname)

    print(f"✅ ZIP selesai → {zip_path}")




# -----------------------------------------------------------
# MODE: Manual (choose exact chapters)
# -----------------------------------------------------------
def mode_manual(series_dir, chapters):
    selection = inquirer.text(
        message="Masukkan daftar chapter (contoh: 1,2,5,10-15):"
    ).execute()

    selected_numbers = parse_selection(selection)
    print(f"→ Chapter terpilih: {selected_numbers}")

    zip_batch(series_dir, chapters, selected_numbers[0], selected_numbers[-1])


# -----------------------------------------------------------
# MODE: Otomatis mulai dari chapter tertentu
# -----------------------------------------------------------
def mode_otomatis(series_dir, chapters):
    chapter_nums = list(chapters.keys())

    start_from = int(inquirer.text(
        message=f"Mulai dari chapter berapa? (tersedia {chapter_nums[0]} sampai {chapter_nums[-1]}):"
    ).execute())

    batch_size = int(inquirer.text(
        message="Sampai chapter berapa? (contoh: 5):"
    ).execute())

    filtered = [c for c in chapter_nums if c >= start_from]

    if not filtered:
        print("❌ Tidak ada chapter di atas angka tersebut.")
        return

    print(f"\n🔄 Mode otomatis: mulai dari {start_from}, batch size = {batch_size}")

    for i in range(0, len(filtered), batch_size):
        batch = filtered[i:i + batch_size]
        start_num, end_num = batch[0], batch[-1]
        zip_batch(series_dir, chapters, start_num, end_num)


# -----------------------------------------------------------
# MODE: Range X–Y
# -----------------------------------------------------------
def mode_range(series_dir, chapters):
    chapter_nums = list(chapters.keys())

    start_range = int(inquirer.text(
        message="Mulai dari chapter berapa? (contoh: 70):"
    ).execute())

    end_range = int(inquirer.text(
        message="Sampai chapter berapa? (contoh: 100):"
    ).execute())

    batch_size = int(inquirer.text(
        message="Kelipatan batch berapa? (contoh: 5):"
    ).execute())

    filtered = [c for c in chapter_nums if start_range <= c <= end_range]

    if not filtered:
        print("❌ Tidak ada chapter pada range tersebut.")
        return

    print(f"\n🔄 Mode range: {start_range}–{end_range}, batch size = {batch_size}")

    for i in range(0, len(filtered), batch_size):
        batch = filtered[i:i + batch_size]
        start_num, end_num = batch[0], batch[-1]
        zip_batch(series_dir, chapters, start_num, end_num)


# -----------------------------------------------------------
# SELECT SERIES FOLDER
# -----------------------------------------------------------
def choose_series_folder(base_dir):
    candidates = [
        p for p in base_dir.rglob("*_result/*")
        if p.is_dir()
    ]

    if not candidates:
        print("❌ Tidak ditemukan folder *_result berisi chapter.")
        return None

    selected = inquirer.select(
        message="Pilih folder series:",
        choices=[str(p) for p in candidates]
    ).execute()

    return Path(selected)


# -----------------------------------------------------------
# MAIN
# -----------------------------------------------------------
if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent

    series_dir = choose_series_folder(base_dir)
    if not series_dir:
        exit()

    chapters = collect_chapters(series_dir)
    if not chapters:
        print("❌ Tidak ada folder chapter ditemukan.")
        exit()

    mode = inquirer.select(
        message="Pilih mode:",
        choices=[
            "Manual (pilih chapter sendiri)",
            "Otomatis (mulai dari chapter tertentu)",
            "Range (zip otomatis dari chapter X sampai Y)",
        ]
    ).execute()

    if mode.startswith("Manual"):
        mode_manual(series_dir, chapters)

    elif mode.startswith("Otomatis"):
        mode_otomatis(series_dir, chapters)

    else:
        mode_range(series_dir, chapters)

    print("\n🎉 Selesai.")
