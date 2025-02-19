import pathlib

def email_file_validate(file):
    if file:
        file_path = pathlib.Path(str(file.filename)).suffix
        allowed_extensions = ['.html', '.txt']

        return file_path in allowed_extensions
    pass

def present_file_validate(file):
    if file:
        file_path = pathlib.Path(str(file.filename)).suffix
        allowed_extensions = ['.html', '.pdf', '.docx', '.pptx', '.pptm', '.xps']

        return file_path in allowed_extensions
    pass

def video_file_validate(file):
    if file:
        file_path = pathlib.Path(str(file.filename)).suffix
        allowed_extensions = ['mp4', 'avi', 'mov', 'mkv']

        return file_path in allowed_extensions
    pass


def photo_file_validate(file):
    if file:
        file_path = pathlib.Path(str(file.filename)).suffix
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.heic', '.webp']

        return file_path in allowed_extensions
    pass