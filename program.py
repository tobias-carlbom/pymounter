import os, sys, getpass, hashlib, base64
from cryptography.fernet import Fernet
import time

CONF = os.path.join(os.path.expanduser("~"),
    "pymounter.dat" if sys.platform == "win32" else ".pymounter.dat")

if sys.platform == "win32":
    UNMOUNT_CMD = 'net use {drive}: /delete /y 2>nul'
    MOUNT_CMD = 'net use {drive}: \\\\{server}\\{share} /user:{username} {password}'
else:
    UNMOUNT_CMD = 'umount -f /Volumes/{share} 2>/dev/null'
    MOUNT_CMD = """osascript -e 'mount volume "smb://{server}/{share}" as user name "{username}" with password "{password}"'"""

def get_key():
    seed = (os.getlogin() + os.path.expanduser("~")).encode()
    return base64.urlsafe_b64encode(hashlib.sha256(seed).digest())

def save(fields):
    f = Fernet(get_key())
    data = "\n".join(fields).encode()
    with open(CONF, "wb") as file:
        file.write(f.encrypt(data))

def load():
    f = Fernet(get_key())
    with open(CONF, "rb") as file:
        data = f.decrypt(file.read())
    return data.decode().split("\n")

def install_autostart(app_path):
    if sys.platform == "win32":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "PyMounter", 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(key)
    else:
        plist_dir = os.path.expanduser("~/Library/LaunchAgents")
        plist_path = os.path.join(plist_dir, "com.carlbomsdata.pymounter.plist")
        os.makedirs(plist_dir, exist_ok=True)
        with open(plist_path, "w") as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.carlbomsdata.pymounter</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>LaunchOnlyOnce</key>
    <true/>
</dict>
</plist>""")
        os.system(f"launchctl load {plist_path}")
    print("Autostart enabled")

def uninstall():
    if sys.platform == "win32":
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "PyMounter")
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass
    else:
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.carlbomsdata.pymounter.plist")
        os.system(f"launchctl unload {plist_path} 2>/dev/null")
        try:
            os.remove(plist_path)
        except FileNotFoundError:
            pass
    try:
        os.remove(CONF)
    except FileNotFoundError:
        pass
    print("Uninstalled: autostart removed, config deleted")
    sys.exit(0)

def setup():
    print("First time setup of SMB share: ")
    print("(Credentials will be AES encrypted on your local PC)")
    fields = [
        input("Server (e.g. 192.168.1.10): "),
        input("Shared folder (e.g. workspace): "),
        input("Username: "),
        getpass.getpass("Password: ")
    ]
    if sys.platform == "win32":
        fields.append(input("Drive letter (e.g. Z): ").strip().upper())
    save(fields)
    print(f"Successfully stored config in {CONF}")
    install_autostart(os.path.abspath(sys.argv[0]))
    print(f"Successfully added to autostart")
    time.sleep(5)
    return fields

if __name__ == "__main__":
    try:
        if "--uninstall" in sys.argv:
            uninstall()

        if os.path.exists(CONF):
            fields = load()
        else:
            fields = setup()

        server = fields[0]
        share = fields[1]
        username = fields[2]
        password = fields[3]
        drive = fields[4] if sys.platform == "win32" else ""

        print("START PROGRAM")
        time.sleep(2)
        resp = os.system(UNMOUNT_CMD.format(share=share, drive=drive))
        if resp != 0:
            print(f"Unmount failed (exit code {resp})")

        time.sleep(2)
        resp = os.system(MOUNT_CMD.format(server=server, share=share, username=username, password=password, drive=drive))
        if resp != 0:
            print(f"Mount failed (exit code {resp})")
        else:
            print(f"Successfully Mounted {share}")

        print("END PROGRAM")
        time.sleep(2)
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)