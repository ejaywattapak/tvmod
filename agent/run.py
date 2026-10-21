#!/usr/bin/env python3
"""
EJWATT TV MOD - agent runner
============================================================
Guna:
    python3 run.py --tv 192.168.0.4:5555
    python3 run.py --tv 192.168.0.4:5555 --uninstall

Apa dia buat:
  1. sambung adb (TCP) ke TV
  2. hantar semua fail ke /data/local/tmp/ejwatt
  3. install app installer (EJWATT TV MOD)
  4. hidupkan shell helper (ejwatt-exec.sh)
  5. buka menu installer kat TV  -> user tick -> tekan MULA INSTALL

by ejaywatt · telegram @ejwtpkvpn
"""
import argparse, importlib.util, os, socket, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load_adb():
    p = os.path.join(HERE, "adbcli.py")
    spec = importlib.util.spec_from_file_location("adbcli", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def push(adb, local, remote, port=9977):
    """Hantar fail ke TV guna nc (adb shell tak sesuai untuk fail besar)."""
    data = open(local, "rb").read()
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(1)
    srv.settimeout(180)
    sent = []

    def serve():
        try:
            c, _ = srv.accept()
            c.sendall(data)
            c.shutdown(socket.SHUT_WR)
            c.close()
            sent.append(True)
        except Exception as e:
            print("  ! push server:", e)
        finally:
            srv.close()

    t = threading.Thread(target=serve)
    t.daemon = True
    t.start()
    adb.shell("nc -w 20 %s %d > %s" % (local_ip(), port, remote), timeout=240)
    t.join(200)
    size = adb.shell("ls -l %s" % remote, timeout=60)
    return size.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tv", required=True, help="ip:port TV, cth 192.168.0.4:5555")
    ap.add_argument("--auth", type=int, default=12)
    ap.add_argument("--no-launch", action="store_true")
    a = ap.parse_args()

    host, _, port = a.tv.partition(":")
    port = int(port or 5555)

    adbmod = load_adb()
    print("[1/5] sambung %s:%d ..." % (host, port))
    adb = None
    last = None
    # percubaan pertama selalunya "gagal" sebab dia hantar public key dulu
    # (TV akan tambah key tu), cubaan kedua terus berjaya.
    for attempt in range(4):
        try:
            adb = adbmod.Adb(host, port, timeout=90)
            banner = adb.connect(auth_timeout=a.auth)
            print("      " + banner.split("\n")[0][:70])
            break
        except Exception as e:
            last = e
            print("      cubaan %d gagal: %s" % (attempt + 1, str(e)[:60]))
            time.sleep(4)
    if adb is None:
        print("\n!! Tak dapat sambung: %s" % last)
        print("   Kalau TV tanya 'Allow USB debugging?', tekan ALLOW guna remote,")
        print("   kemudian jalankan arahan ni sekali lagi.")
        sys.exit(2)

    print("[2/5] sediakan folder")
    adb.shell("mkdir -p /data/local/tmp/ejwatt", timeout=60)

    files = [
        (os.path.join(ROOT, "apks", "tvhome.apk"), "/data/local/tmp/ejwatt/tvhome.apk"),
        (os.path.join(ROOT, "apks", "animedream.apk"), "/data/local/tmp/ejwatt/animedream.apk"),
        (os.path.join(ROOT, "helper", "ejwatt-exec.sh"), "/data/local/tmp/ejwatt/ejwatt-exec.sh"),
        (os.path.join(ROOT, "helper", "bloat.txt"), "/data/local/tmp/ejwatt/bloat.txt"),
    ]
    for i, (local, remote) in enumerate(files):
        print("      push %-22s ..." % os.path.basename(local), end=" ")
        sys.stdout.flush()
        out = push(adb, local, remote, port=9977 + i)
        print(out[:60])

    print("[3/5] install app installer")
    adb.shell("mkdir -p /data/local/tmp/ejwatt", timeout=60)
    apk = os.path.join(ROOT, "installer", "ejwatt-installer.apk")
    print("      push ejwatt-installer.apk ...", end=" ")
    sys.stdout.flush()
    print(push(adb, apk, "/data/local/tmp/ejwatt/ejwatt-installer.apk", port=9985)[:60])
    print("      pm install:", adb.shell(
        "pm install -r -d /data/local/tmp/ejwatt/ejwatt-installer.apk", timeout=240).strip())

    print("[4/5] hidupkan shell helper")
    adb.shell("chmod 755 /data/local/tmp/ejwatt/ejwatt-exec.sh", timeout=60)
    adb.shell("pkill -f ejwatt-exec.sh; sleep 1", timeout=60)
    adb.shell("nohup setsid sh /data/local/tmp/ejwatt/ejwatt-exec.sh "
              ">/dev/null 2>&1 & sleep 3; echo started", timeout=90)
    time.sleep(2)
    alive = adb.shell("ps -A -o ARGS | grep ejwatt-exec | grep -v grep", timeout=60)
    print("      helper:", "AKTIF" if "ejwatt-exec" in alive else "GAGAL (cuba lagi)")

    if not a.no_launch:
        print("[5/5] buka menu installer kat TV")
        print("      " + adb.shell(
            "am start -n com.ejay.tvmodinstaller/.InstallActivity", timeout=90).strip())

    print("\nSiap. Kat TV sekarang ada menu EJWATT TV MOD.")
    print("Tick apa yang nak, pastu tekan MULA INSTALL (guna remote).")


if __name__ == "__main__":
    main()
