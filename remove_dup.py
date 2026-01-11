import os
import hashlib
import shutil

# Music file extensions
MUSIC_EXTENSIONS = ('.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg')

def get_file_hash(file_path, chunk_size=8192):
    """Generate SHA256 hash for a file"""
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def move_duplicate_music(source_folder, duplicate_folder):
    hash_map = {}
    moved_files = 0

    os.makedirs(duplicate_folder, exist_ok=True)

    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(MUSIC_EXTENSIONS):
                full_path = os.path.join(root, file)
                file_hash = get_file_hash(full_path)

                if not file_hash:
                    continue

                if file_hash in hash_map:
                    destination = os.path.join(duplicate_folder, file)

                    # Avoid overwriting files with same name
                    base, ext = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(destination):
                        destination = os.path.join(
                            duplicate_folder, f"{base}_{counter}{ext}"
                        )
                        counter += 1

                    shutil.move(full_path, destination)
                    print(f"📦 Moved duplicate → {destination}")
                    moved_files += 1
                else:
                    hash_map[file_hash] = full_path

    print(f"\n✅ Completed! Moved {moved_files} duplicate music files.")

if __name__ == "__main__":
    source = "o_music"
    duplicates = "d_music"

    if os.path.isdir(source):
        move_duplicate_music(source, duplicates)
    else:
        print("❌ Invalid source folder path")
