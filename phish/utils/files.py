from phish.utils.generator import generate_short_uuid
import shutil
import os


def save_file(file, folder_name):
    if file:
        folder_path = f"/phish/upload_files/{folder_name}/"
        os.makedirs(folder_path, exist_ok=True)
        file_location = os.path.join(folder_path, f"{generate_short_uuid()}-{file.filename}")

        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        return file_location
    return False