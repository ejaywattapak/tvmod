#!/system/bin/sh
# ============================================================
#  EJWATT TV MOD - shell helper (jalan sebagai uid shell)
#  Dia tengok plan.txt dari app installer, buat kerja, tulis status.txt
#  by ejaywatt  ·  telegram @ejwtpkvpn
# ============================================================
DIR=/sdcard/Android/data/com.ejay.tvmodinstaller/files
APK=/data/local/tmp/ejwatt
PLAN=$DIR/plan.txt
STATUS=$DIR/status.txt
ALIVE=$DIR/alive.txt
LOG=/data/local/tmp/ejwatt-exec.log

log(){ echo "$(date +%H:%M:%S) $*" >> $LOG; }

have(){ pm list packages 2>/dev/null | grep -q "package:$1"; }

say(){ echo "$1" >> $STATUS; log "$1"; }

# jalankan pm install, output ringkas
inst(){
  out=$(pm install -r -d "$1" 2>&1)
  case "$out" in
    *Success*) return 0 ;;
    *) echo "$out" >> $LOG; return 1 ;;
  esac
}

do_launcher(){
  if inst $APK/tvhome.apk; then say "launcher :: OK"; else say "launcher :: GAGAL install"; return; fi
  # set sebagai home
  if cmd package set-home-activity com.mihir.tvhome/.MainActivity >/dev/null 2>&1; then
    say "launcher :: jadi home default"
  else
    am start -a android.intent.action.MAIN -c android.intent.category.HOME >/dev/null 2>&1
    say "launcher :: set home (fallback)"
  fi
  for p in com.google.android.apps.tv.launcherx com.google.android.tungsten.setupwraith; do
    if have $p; then pm disable-user --user 0 $p >/dev/null 2>&1 && log "disable $p"; fi
  done
  say "launcher :: launcher stock dimatikan"
}

do_debloat(){
  n=0
  if [ -f $APK/bloat.txt ]; then
    while read -r p; do
      case "$p" in ''|\#*) continue ;; esac
      if have $p; then
        pm disable-user --user 0 $p >/dev/null 2>&1 && n=$((n+1)) && log "bloat off $p"
      fi
    done < $APK/bloat.txt
  fi
  say "debloat :: $n app dimatikan"
}

do_cleaner(){
  am broadcast -a com.ejay.START_CLEANER -n com.ejay.animedream/.Boot >/dev/null 2>&1
  if [ $? -eq 0 ]; then say "cleaner :: AKTIF (10 min sekali)"; else say "cleaner :: GAGAL"; fi
}

do_dream(){
  if inst $APK/animedream.apk; then
    settings put secure screensaver_components com.ejay.animedream/.AnimeDream
    settings put secure screensaver_enabled 1
    settings put secure screensaver_activate_on_sleep 1
    say "screensaver :: OK (jam/tarikh/network)"
  else
    say "screensaver :: GAGAL install"
  fi
}

do_cfg(){
  w=$1; p=$2; a=$3
  am broadcast -a com.ejay.ANIMEDREAM_CFG -n com.ejay.animedream/.Cfg \
     --ez wallpaper $w --ez prayer $p --ez ayah $a >/dev/null 2>&1
  say "addon :: wallpaper=$w prayer=$p ayah=$a"
}

run_plan(){
  : > $STATUS
  say "== EJWATT TV MOD =="
  grep -q '^launcher=1' $PLAN && do_launcher
  grep -q '^debloat=1'  $PLAN && do_debloat
  grep -q '^cleaner=1'  $PLAN && do_cleaner
  if grep -q '^dream=1' $PLAN; then
    do_dream
    W=0; P=0; A=0
    grep -q '^wallpaper=1' $PLAN && W=1
    grep -q '^prayer=1'    $PLAN && P=1
    grep -q '^ayah=1'      $PLAN && A=1
    do_cfg $W $P $A
  fi
  say "DONE"
  rm -f $PLAN
}

mkdir -p $DIR 2>/dev/null
log "helper start pid=$$"
while true; do
  date +%s > $ALIVE
  if [ -f $PLAN ]; then
    log "plan detected"
    run_plan
  fi
  sleep 2
done
