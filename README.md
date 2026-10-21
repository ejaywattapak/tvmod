<div align="center">

# EJWATT TV MOD

**A menu-based installer for Android TV. Select features, then install.**

![Version](https://img.shields.io/badge/version-1.0-00e5ff?style=for-the-badge)
![Android TV](https://img.shields.io/badge/Android%20TV-5.0%2B-7c4dff?style=for-the-badge)
![Root](https://img.shields.io/badge/root-not%20required-00c853?style=for-the-badge)

[Telegram: @ejwtpkvpn](https://t.me/ejwtpkvpn)

</div>

## What It Does

EJWATT TV MOD runs on your Android TV and provides a simple menu to install or configure selected features without root access. It requires ADB network debugging to be enabled.

- **TVHome Launcher** — a cleaner app launcher.
- **Bloatware removal** — disables selected apps; edit `helper/bloat.txt` to change the list.
- **Auto Cleaner** — periodically clears cache and stops background apps.
- **Custom screensaver** — clock, date, Wi-Fi details, rotating anime wallpapers, JAKIM prayer times, and a daily Quran verse.

## What's Included

- `installer/ejwatt-installer.apk` — installer menu.
- `apks/tvhome.apk` — TV launcher.
- `apks/animedream.apk` — screensaver and cleaner.
- `helper/ejwatt-exec.sh` — shell helper that applies selected actions.
- `helper/bloat.txt` — configurable list of apps to disable.
- `agent/run.py` and `agent/adbcli.py` — installation runner and ADB client.

## Install

1. Extract `ejwattTVMOD.zip` on your computer and connect it to the same network as your TV.
2. On the TV, enable **Developer options** (open **Settings → Device Preferences → About** and select **Build** seven times), then enable **Network debugging**. Approve the debugging prompt if it appears.
3. Open a terminal in the extracted folder and run the command below. Replace the example address with your TV's IP address.

```bash
unzip ejwattTVMOD.zip -d ejwattTVMOD
cd ejwattTVMOD
python3 agent/run.py --tv 192.168.1.100:5555
```

When the installer opens on your TV, select the features you want and choose **Start Install**.
