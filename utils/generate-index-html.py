import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_index_from_template(output_folder):
    template_path = os.path.join(BASE_DIR, "template", "index.html")

    if not os.path.exists(template_path):
        print("[ERROR] Template index.html tidak ditemukan!")
        return

    images = sorted([
        f for f in os.listdir(output_folder)
        if f.lower().endswith(".jpg")
    ])

    json_path = os.path.join(output_folder, "list.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(images, jf, indent=4)
    print("[OK] list.json dibuat")

    output_html = os.path.join(output_folder, "index.html")
    shutil.copyfile(template_path, output_html)

