def get_platform():
    import platform
    return platform.system()

def is_windows():
    return get_platform() == "Windows"

def is_linux():
    return get_platform() == "Linux"

def get_path_separator():
    return "\\" if is_windows() else "/"

def normalize_path(path):
    return path.replace("/", get_path_separator()).replace("\\", get_path_separator())