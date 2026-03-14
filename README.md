# PyMounter

SMB share mounter for macOS and Windows. Automatically mounts a network share at login.

**[Download latest release](https://github.com/tobias-carlbom/pymounter/releases/latest)**

## Features

- First-time setup wizard with AES-encrypted credential storage
- Automatic login item registration (macOS LaunchAgent / Windows Registry)
- Cross-platform: macOS (.app bundle) and Windows (.exe)
- Clean uninstall via `--uninstall` flag

## Quick Start

Run the binary once to configure:

```
$ ./PyMounter
First time setup of SMB share:
Credentials will be AES encrypted locally.
Server (e.g. 192.168.1.10): 192.168.1.10
Shared folder (e.g. workspace): workspace
Username: username
Password:
Successfully stored config in /Users/username/.pymounter.dat
Autostart enabled
```

After setup, the share mounts automatically at every login.

## Uninstall

```
./PyMounter --uninstall
```

Removes autostart and deletes the encrypted config file.

## Build

Requires Python 3.13, Nuitka, cryptography, and make:

```
pip install 'nuitka[onefile]' cryptography
```

Then:

```
make clean && make
```

Output:

- macOS: `build/PyMounter.app`
- Windows: `build/PyMounter.exe`

## File Locations

|       |Config                       |Autostart                                                |
|-------|-----------------------------|---------------------------------------------------------|
|macOS  |`~/.pymounter.dat`           |`~/Library/LaunchAgents/com.carlbomsdata.pymounter.plist`|
|Windows|`%USERPROFILE%\pymounter.dat`|`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`     |

## License

MIT