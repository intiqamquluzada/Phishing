import os
import shutil
from urllib.parse import urljoin
from fastapi import Request
from utils.generator import generate_short_uuid
import main


def save_file(file, request: Request):
    if file:
        os.makedirs(main.upload_folder, exist_ok=True)
        filename = file.filename.replace(" ", "")
        file_name = f"{generate_short_uuid()}-{filename}"
        file_location = os.path.join(main.upload_folder, file_name)

        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        base_url = str(request.base_url)
        file_url = urljoin(base_url, file_location)

        return file_url
    return None
