#!/usr/bin/env bash
set -euo pipefail
package=org.scape2003.mudclient.offline
mkdir -p android-test
adb install -r org.scape2003.mudclient/app/build/outputs/apk/offline/debug/app-offline-debug.apk
adb shell wm size 480x800
adb shell settings put system accelerometer_rotation 0
adb shell settings put system user_rotation 1
adb shell settings put global airplane_mode_on 1
adb shell svc wifi disable
adb shell svc data disable
adb logcat -c
adb shell am start -n "$package/org.scape2003.mudclient.mudclientActivity"
sleep 20
adb exec-out screencap -p > android-test/01-welcome.png
adb shell input tap 400 357
sleep 30
adb exec-out screencap -p > android-test/02-character.png
adb shell input tap 400 383
sleep 15
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
    print('PASS: Android world started with internet disabled; character and starter inventory persisted',row)
PY
