def safe_file_name(file_name):
    if ".." in file_name:
        raise ValueError(f"{file_name} is not an allowed path")
    return True
