import os
import shutil
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

SOURCE_FOLDER = "d_music"
DEST_FOLDER = os.path.join(SOURCE_FOLDER, "Tamil")

os.makedirs(DEST_FOLDER, exist_ok=True)

def safe_name(text):
    return "".join(c for c in text if c not in r'\/:*?"<>|').strip()

organized = 0
skipped = 0

for root, _, files in os.walk(SOURCE_FOLDER):
    for file in files:
        if not file.lower().endswith(".mp3"):
            continue

        full_path = os.path.join(root, file)

        try:
            audio = MP3(full_path, ID3=EasyID3)

            artist = audio.get("artist", ["Unknown Artist"])[0]
            title = audio.get("title", [None])[0]

            if not title:
                print(f"⚠️ Skipping (no title): {file}")
                skipped += 1
                continue

            artist = safe_name(artist)
            title = safe_name(title)

            artist_folder = os.path.join(DEST_FOLDER, artist)
            os.makedirs(artist_folder, exist_ok=True)

            new_name = f"{artist} - {title}.mp3"
            new_path = os.path.join(artist_folder, new_name)

            if not os.path.exists(new_path):
                shutil.move(full_path, new_path)
                organized += 1

        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
            skipped += 1

print("\n✅ ORGANIZATION COMPLETE")
print(f"🎵 Organized songs: {organized}")
print(f"⚠️ Skipped songs: {skipped}")
