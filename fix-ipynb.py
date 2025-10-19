import os
import base64
import json
from pathlib import Path

# ==== CONFIG ====
NOTEBOOKS_DIR = Path("ipynb")          # Folder containing your notebooks
SCREENSHOTS_DIR = Path("screenshots")  # Folder at project root
# =================

def extract_and_update_attachments(nb_path: Path):
    """Extract embedded image attachments and update markdown references."""
    try:
        # Skip empty files
        if nb_path.stat().st_size == 0:
            print(f"⚠️ Skipping empty file: {nb_path}")
            return

        with open(nb_path, "r", encoding="utf-8") as f:
            nb_data = json.load(f)
    except json.JSONDecodeError:
        print(f"⚠️ Skipping invalid JSON file: {nb_path}")
        return
    except Exception as e:
        print(f"❌ Error reading {nb_path}: {e}")
        return

    attachments_found = False

    for cell in nb_data.get("cells", []):
        if "attachments" in cell:
            attachments = cell["attachments"]
            for filename, attachment in attachments.items():
                for mime, b64data in attachment.items():
                    if mime.startswith("image/"):
                        # Ensure screenshots directory exists
                        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
                        safe_filename = filename.replace(" ", "_")
                        out_path = SCREENSHOTS_DIR / safe_filename

                        try:
                            with open(out_path, "wb") as img_file:
                                img_file.write(base64.b64decode(b64data))
                        except Exception as e:
                            print(f"❌ Error saving image {safe_filename}: {e}")
                            continue

                        # Update markdown to relative path
                        cell["source"] = [
                            line.replace(f"(<attachment:{filename}>)",
                                         f"(../screenshots/{safe_filename})")
                            for line in cell["source"]
                        ]
                        attachments_found = True

            # Remove attachments to clean notebook JSON
            del cell["attachments"]

    if attachments_found:
        backup_path = nb_path.with_suffix(".ipynb.bak")
        os.rename(nb_path, backup_path)
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(nb_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated {nb_path.name}, backup saved as {backup_path.name}")
    else:
        print(f"— No attachments found in {nb_path.name}")

def main():
    NOTEBOOKS_DIR_PATH = Path(NOTEBOOKS_DIR)
    for nb_file in NOTEBOOKS_DIR_PATH.rglob("*.ipynb"):
        extract_and_update_attachments(nb_file)

if __name__ == "__main__":
    main()
