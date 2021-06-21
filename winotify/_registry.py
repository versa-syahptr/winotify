import winreg

HKEY = winreg.HKEY_CURRENT_USER
SUBKEY = r"SOFTWARE\Classes\{}"


def key_exist(app: str) -> bool:
    try:
        k = winreg.OpenKey(HKEY, SUBKEY.format(app))
        winreg.CloseKey(k)
        return True
    except WindowsError:
        return False


def register(app: str, full_path: str):
    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    app = format_name(app)

    if not key_exist(app):
        key = winreg.CreateKey(reg, SUBKEY.format(app))
        # try:
        with key:
            print(1)
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f"URL:{app}")
            print(2)
            winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, '')
            print(3)
            subkey = winreg.CreateKey(key, r"shell\open\command")
            print(4)
            with subkey:
                print(5)
                winreg.SetValueEx(subkey, '', 0, winreg.REG_SZ, f"{full_path} %1")
                print(6)


def format_name(name: str):
    return name.replace(' ', '-')
