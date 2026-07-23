import os


def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def delete_file_if_exists(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
