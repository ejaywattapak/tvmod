# AGENT.md — arahan untuk AI agent

Fail ni untuk **AI agent** (Zafiro / Claude / apa-apa shell agent) yang dapat zip ni
dan diminta "install kat TV". Ikut langkah ni exactly, jangan teka.

## 0. Fakta asas

- TV dijangkakan ada **ADB over TCP** (`ip:5555`). Kalau tak tahu IP, scan port 5555 dalam LAN.
- Semua kerja dibuat sebagai uid **shell** (bukan root). `pm install`, `settings put`,
  `pm disable-user` semua dibenarkan untuk shell.
- App installer tak boleh install APK sendiri → dia tulis plan, helper yang buat.

## 1. Jalankan driver

```bash
python3 agent/run.py --tv <IP_TV>:5555
```

Output dijangka:

```text
[1/5] sambung 192.168.0.4:5555 ...
[2/5] sediakan folder
      push tvhome.apk           ... -rw-rw-rw- 9291125
      push animedream.apk       ... -rw-rw-rw- 9287084
      push ejwatt-exec.sh       ... -rw-rw-rw- 3130
      push bloat.txt            ... -rw-rw-rw- 374
[3/5] install app installer
      pm install: Success
[4/5] hidupkan shell helper
      helper: AKTIF
[5/5] buka menu installer kat TV
      Starting: Intent { cmp=com.ejay.tvmodinstaller/.InstallActivity }
```

Kalau `helper: GAGAL`, ulang:

```bash
adb shell "nohup setsid sh /data/local/tmp/ejwatt/ejwatt-exec.sh >/dev/null 2>&1 &"
```

## 2. Kalau ADB minta kebenaran

`AdbError: timed out: allow dialog not accepted on the TV?`
→ **dialog "Allow USB debugging?" sedang keluar kat TV**. Minta user tekan **Allow**
guna remote (tick *Always allow from this computer*). Lepas tu ulang arahan.

Cara pastikan port hidup:

```bash
adb connect <IP_TV>:5555
adb devices      # patut keluar device, bukan unauthorized
```

## 3. Lepas menu keluar

**JANGAN** tick apa-apa untuk user. Biar user pilih sendiri.
Kalau user minta "install semua", tick semua (default memang semua tick).

Untuk verify hasil selepas user tekan MULA INSTALL:

```bash
adb shell cat /sdcard/Android/data/com.ejay.tvmodinstaller/files/status.txt
adb shell cat /data/local/tmp/ejwatt-exec.log
adb shell dumpsys package com.ejay.animedream | grep versionName
adb shell settings get secure screensaver_components
adb shell cmd package resolve-activity --brief -c android.intent.category.HOME | tail -1
```

Dijangka:

```text
== EJWATT TV MOD ==
launcher :: OK
launcher :: jadi home default
debloat :: 4 app dimatikan
cleaner :: AKTIF (10 min sekali)
screensaver :: OK (jam/tarikh/network)
addon :: wallpaper=1 prayer=1 ayah=1
DONE
```

## 4. Trigger tanpa UI (headless)

Kalau user tak nak guna menu, tulis plan sendiri:

```bash
adb shell "cat > /sdcard/Android/data/com.ejay.tvmodinstaller/files/plan.txt <<'EOF'
launcher=1
debloat=1
cleaner=1
dream=1
wallpaper=1
prayer=1
ayah=1
EOF"
```

Helper akan proses dalam ~2 saat. Semak `status.txt`.

## 5. Jangan buat

- Jangan `pm disable-user` pakej sistem teras (`com.android.systemui`, `com.android.tv.settings`,
  `com.google.android.gms`, `com.android.providers.*`) — TV boleh jadi brick/UI hilang.
- Jangan guna `pm uninstall` untuk app sistem; guna `pm disable-user` sahaja.
- Jangan restart TV semasa install.

---

by ejaywatt · [@ejwtpkvpn](https://t.me/ejwtpkvpn)
