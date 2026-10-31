#!/usr/bin/env bash
set -euo pipefail
package=org.scape2003.mudclient.offline
mkdir -p android-test
trap 'adb logcat -d > android-test/logcat.txt' EXIT
function tap_button() {
    read -r x y < <(python3 - "$1" "$2" <<'PYCODE'
import struct,sys
w,h=struct.unpack('>II',open(sys.argv[1],'rb').read()[16:24])
compact=w<512 or h<346
# SDL stretches its logical surface to the emulator display.
print(w//2, round(h * (0.83 if sys.argv[2]=='play' else 0.92)))
PYCODE
)
    adb shell input tap "$x" "$y"
}
adb install -r org.scape2003.mudclient/app/build/outputs/apk/offline/debug/app-offline-debug.apk
adb shell wm size 480x800
adb shell settings put system accelerometer_rotation 0
adb shell settings put system user_rotation 1
adb shell settings put global airplane_mode_on 1
adb shell svc wifi disable
adb shell svc data disable
adb logcat -c
# Simulate an interrupted installation: the marker exists but the service's
# required configuration is absent. Retry must remain possible afterward.
adb shell run-as "$package" mkdir -p files/world-2001
adb shell run-as "$package" touch files/world-2001/.assets-v2
adb shell am start -n "$package/org.scape2003.mudclient.mudclientActivity"
sleep 20
adb exec-out screencap -p > android-test/01-welcome.png
tap_button android-test/01-welcome.png play
# The service cannot load its deliberately missing configuration. Wait for
# the bounded startup deadline and verify that the app reports the failure.
failed=0
for attempt in $(seq 1 60); do
    if adb logcat -d -s OfflineWorld:E | grep -q 'Local world start timed out'; then
        failed=1
        break
    fi
    sleep 1
done
test "$failed" = 1
sleep 2
adb exec-out screencap -p > android-test/02-start-failed.png
# Repair the missing asset marker and retry via the same user-visible button.
adb shell run-as "$package" rm files/world-2001/.assets-v2
tap_button android-test/02-start-failed.png play
logged_in=0
for attempt in $(seq 1 90); do
    if adb logcat -d -s SDL/APP:I | grep -q 'Login response: 0'; then
        logged_in=1
        break
    fi
    sleep 1
done
test "$logged_in" = 1
adb exec-out screencap -p > android-test/02-character.png
tap_button android-test/02-character.png accept
sleep 15
adb logcat -d -s AmbientAudio:I '*:S' | grep -q 'Forest ambience playing'
adb exec-out screencap -p > android-test/03-world.png
adb logcat -d > android-test/logcat.txt
adb shell am force-stop "$package"
for name in rsc.sqlite rsc.sqlite-wal; do
    adb exec-out run-as "$package" cat "files/world-2001/$name" > "android-test/$name" || true
done
python3 - <<'PY'
import sqlite3
with sqlite3.connect('android-test/rsc.sqlite') as db:
    row=db.execute('select username,login_date,rpg_class from players').fetchone()
    assert row and row[1]>0 and row[2]!=255, f'Offline character creation/login failed: {row}'
    assert db.execute('select count(*) from players_inventory').fetchone()[0]>0
    print('PASS: startup failure and retry; offline character and starter inventory persisted',row)
PY
# Reopen the installed app without deleting its data and resume the same save.
adb logcat -c
adb shell am start -n "$package/org.scape2003.mudclient.mudclientActivity"
sleep 15
adb exec-out screencap -p > android-test/04-relaunch.png
tap_button android-test/04-relaunch.png play
resumed=0
for attempt in $(seq 1 90); do
    if adb logcat -d -s SDL/APP:I | grep -q 'Login response: 0'; then
        resumed=1
        break
    fi
    sleep 1
done
test "$resumed" = 1
sleep 5
adb logcat -d -s AmbientAudio:I '*:S' | grep -q 'Forest ambience playing'
adb exec-out screencap -p > android-test/05-resumed.png
echo 'PASS: offline character resumed after restarting the app'
