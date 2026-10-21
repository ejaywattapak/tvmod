<div align="center">
  <img src="assets/banner.svg" width="100%" alt="EJWATT TV MOD"/>
  <br/><br/>

  ![version](https://img.shields.io/badge/version-1.0-00e5ff?style=for-the-badge)
  ![platform](https://img.shields.io/badge/Android%20TV-5.0%2B-7c4dff?style=for-the-badge)
  ![root](https://img.shields.io/badge/root-TAK%20PERLU-00ffa3?style=for-the-badge)
  ![telegram](https://img.shields.io/badge/telegram-%40ejwtpkvpn-229ED9?style=for-the-badge&logo=telegram&logoColor=white)

  <h3>Installer ber-menu untuk Android TV — pilih, tick, install.</h3>
  <p><b>by <a href="https://t.me/ejwtpkvpn">ejaywatt</a></b></p>
</div>

---

## 📺 Apa ni?

**EJWATT TV MOD** ialah satu installer ber-menu yang jalan **kat TV sendiri**. Kau tak payah hafal command —
buka app, tick apa yang kau nak, tekan **MULA INSTALL**. Siap.

Semua kerja berat (install APK, disable bloatware, tukar setting) dibuat oleh **shell helper**,
jadi **tak perlu root** dan tak perlu klik satu-satu dialog installer Android.

```text
   ┌──────────────────────────────────────────────┐
   │  EJWATT                                      │
   │  TV MOD INSTALLER                            │
   │  pilih apa yang kau nak  ·  by @ejwtpkvpn     │
   │  ● HELPER AKTIF — sedia install               │
   │  Xiaomi MiTV-MOOR2 · Android 11 · 1920x1080   │
   ├──────────────────────────────────────────────┤
   │  [✔] TVHOME LAUNCHER                         │
   │  [✔] BUANG BLOATWARE                         │
   │  [✔] AUTO CLEANER                            │
   │  [✔] SCREENSAVER EJWATT                      │
   │      [✔] Anime Wallpaper                     │
   │      [✔] Kad Waktu Solat                     │
   │      [✔] Ayat Quran Harian                   │
   │                                              │
   │            ( MULA INSTALL )                  │
   │                                              │
   │  launcher :: OK                              │
   │  debloat  :: 4 app dimatikan                 │
   │  cleaner  :: AKTIF (10 min sekali)           │
   │  screensaver :: OK                           │
   │  DONE                                        │
   └──────────────────────────────────────────────┘
```

---

## ⚡ Apa yang boleh dipilih

| # | Modul | Apa dia buat | Default |
|---|-------|--------------|:-------:|
| 1 | **TVHOME LAUNCHER** | Ganti launcher default dengan `tvhome` (grid app bersih + pills Settings/Inputs/WiFi). Launcher stock auto-dimati. | ✔ |
| 2 | **BUANG BLOATWARE** | Disable app sampah yang TV tak perlu (setup wizard, Play Movies, dl). Senarai boleh edit dalam `helper/bloat.txt`. | ✔ |
| 3 | **AUTO CLEANER** | Foreground service: bunuh app background + clear cache + GC **setiap 10 minit**, keluar popup `cache clear ✅`. | ✔ |
| 4 | **SCREENSAVER EJWATT** | Screensaver custom: jam besar, tarikh, SSID/WiFi, dan waktu solat. | ✔ |
| 4a | ↳ **Anime Wallpaper** | 12 wallpaper anime 4K, rotate automatik. | ✔ |
| 4b | ↳ **Kad Waktu Solat** | Jadual JAKIM (SBH07 · Tuaran), highlight waktu seterusnya. | ✔ |
| 4c | ↳ **Ayat Quran Harian** | 1 ayat sehari (Arab + maksud Melayu), tukar ikut hari. | ✔ |

> Tak tick = tak install. Kau boleh install semula bila-bila dengan pilihan lain.

---

## 🚀 Cara guna (AI agent / terminal)

Cara paling senang — suruh AI agent kau (atau kau sendiri) jalankan:

```bash
unzip ejwattTVMOD.zip -d ejwattTVMOD
cd ejwattTVMOD
python3 agent/run.py --tv 192.168.0.4:5555
```

`run.py` akan buat semua:

1. sambung ADB ke TV (`ip:5555`)
2. hantar semua fail ke `/data/local/tmp/ejwatt`
3. install app **EJWATT TV MOD**
4. hidupkan **shell helper** (tanpa root)
5. buka **menu installer** kat TV

Lepas tu ambil remote, tick pilihan, tekan **MULA INSTALL**. Siap.

<details>
<summary><b>Kalau TV tanya “Allow USB debugging?”</b></summary>

Tekan **Allow** (dan tick *Always allow from this computer*) guna remote.
Kalau dialog tak keluar, pergi **Settings → Device Preferences → About →** tekan *Build* 7 kali,
kemudian **Developer options → USB debugging / Network debugging → ON**.

</details>

<details>
<summary><b>Manual (tanpa run.py)</b></summary>

```bash
ADB="adb -s 192.168.0.4:5555"
$ADB shell mkdir -p /data/local/tmp/ejwatt

$ADB push apks/tvhome.apk              /data/local/tmp/ejwatt/
$ADB push apks/animedream.apk          /data/local/tmp/ejwatt/
$ADB push helper/ejwatt-exec.sh        /data/local/tmp/ejwatt/
$ADB push helper/bloat.txt             /data/local/tmp/ejwatt/

$ADB install -r installer/ejwatt-installer.apk

$ADB shell chmod 755 /data/local/tmp/ejwatt/ejwatt-exec.sh
$ADB shell "nohup setsid sh /data/local/tmp/ejwatt/ejwatt-exec.sh >/dev/null 2>&1 &"
$ADB shell am start -n com.ejay.tvmodinstaller/.InstallActivity
```

</details>

---

## 🧠 Macam mana ia jalan (tanpa root)

```text
   ┌────────────────────┐        plan.txt        ┌─────────────────────┐
   │  INSTALLER APP     │  ───────────────────►  │  SHELL HELPER       │
   │  (menu + checkbox) │                        │  (uid shell, adb)   │
   │                    │  ◄───────────────────  │                     │
   └────────────────────┘       status.txt       └──────────┬──────────┘
            │                                               │
            │  tunjuk progress ✔                            │ pm install / settings put
            ▼                                               ▼ pm disable-user
        skrin TV                                       TV berubah
```

- App installer **tak boleh** install APK sendiri (Android halang) — jadi dia tulis `plan.txt`.
- Helper (`ejwatt-exec.sh`) yang jalan sebagai uid `shell` baca plan tu dan buat kerja sebenar.
- Helper tulis `status.txt`, app poll dan papar satu-satu `OK / GAGAL`.
- Fail komunikasi: `/sdcard/Android/data/com.ejay.tvmodinstaller/files/`

---

## 📦 Isi dalam zip

```text
ejwattTVMOD.zip
├── README.md                  ← fail ni
├── AGENT.md                   ← arahan untuk AI agent
├── LICENSE
├── assets/banner.svg          ← banner beranimasi
├── installer/ejwatt-installer.apk   (16 KB, menu UI)
├── apks/tvhome.apk                  (launcher, minSdk 21)
├── apks/animedream.apk              (screensaver + auto cleaner, minSdk 21)
├── helper/ejwatt-exec.sh            (shell helper)
├── helper/bloat.txt                 (senarai bloat — boleh edit)
└── agent/
    ├── run.py                       (driver satu arahan)
    └── adbcli.py                    (adb client pure-python)
```

---

## ✅ Support

| Perkara | Status |
|---|---|
| Android TV 5.0 – 14 (API 21+) | ✅ installer, launcher & screensaver dibina `minSdk 21` |
| TV box / Google TV / MiTV / TCL / Sony | ✅ guna komponen standard (Leanback + DreamService) |
| Root | ❌ tak perlu langsung |
| Resolusi | ✅ 720p / 1080p / 4K — semua saiz guna `dp`/`sp` |
| TV tanpa network debugging | ⚠️ perlu hidupkan ADB dulu (rujuk atas) |

> Deria sebenar: diuji pada **Xiaomi MiTV-MOOR2 (Android 11, 1080p)**.

---

## 🧹 Nak buang / restore

```bash
# buang app
adb shell pm uninstall com.ejay.tvmodinstaller com.ejay.animedream com.mihir.tvhome

# hidupkan balik launcher stock
adb shell pm enable com.google.android.apps.tv.launcherx
adb shell cmd package set-home-activity com.google.android.apps.tv.launcherx/.HomeActivity

# hidupkan balik bloat yang didisable
adb shell pm enable com.google.android.videos
```

---

## 🐞 Troubleshooting

| Masalah | Penyelesaian |
|---|---|
| Menu tak keluar | `adb shell am start -n com.ejay.tvmodinstaller/.InstallActivity` |
| Tulis **HELPER TIADA** | helper mati (TV restart) — jalankan `run.py` semula |
| Item tulis `GAGAL` | tengok log: `adb shell cat /data/local/tmp/ejwatt-exec.log` |
| Screensaver tak jadi | `adb shell settings get secure screensaver_components` mesti `com.ejay.animedream/.AnimeDream` |
| Popup `cache clear` tak keluar | `adb shell am broadcast -a com.ejay.START_CLEANER -n com.ejay.animedream/.Boot` |

---

<div align="center">

### 💬 Contact

Ada bug / nak request? Telegram aku: **[@ejwtpkvpn](https://t.me/ejwtpkvpn)**

`EJWATT TV MOD` · dibuat oleh **ejaywatt** untuk TV yang buat hal sendiri 🤙

<sub>MIT License · guna dengan risiko sendiri</sub>

</div>
