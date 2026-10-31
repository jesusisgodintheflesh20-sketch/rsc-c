# RSC Offline (2001)

An Android-only, separate app flavor for the December 10, 2001 free-to-play world.
Tap **Play / Continue offline**, design your character on first launch, then play.
No account entry or internet connection is needed. The existing online flavor is retained.
This is an emulation of the original game, not Jagex's original server source.

## Engine and data

RSC Sundae from https://github.com/hikilaka/RSCSundae at
`afed29c3ba76c52695ee350980e0df012762ad73`, public domain (vendor/COPYING).
All upstream world scripts and spawns are bundled, including quests, skills,
combat, shops, banks, NPC dialogue and inventory rules.
The 2003/modern members game is outside this flavor's scope.

The server runs in the app's non-exported `:offline` service process, listening
only on 127.0.0.1:43595. SDL connects using an automatically created local
Adventurer character over the original RSA/ISAAC protocol. The service has a
separate working directory and native globals; it cannot change the client's cwd.
Assets and scripts are extracted on first use and refreshed when the bundled asset version changes. Existing save databases are preserved. There are no runtime downloads.
Both client and server use matching 2001 definitions and maps. The server
archive uses its original text format; `tools/client_config.py` reproducibly
converts those tables to binary client format, using texture names from the
existing visual pack. Original server archives are verified against
upstream's published SHA-256 checksums:

- config46.jag: 304ff7147a21119c4e47f913f5d27d65de8222d69d2f3317dff569d8a4061e94
- maps27.jag: 3061da9b367ce0f6a21c94e7c74a016df49eed2ed274bae2a732d47a9655009b

Archive sources are recorded in vendor/data/fetch-jag-files.sh. Dependency
versions, source URLs and archive hashes are recorded in deps/SOURCES.txt.
Redistribution notices are bundled in the APK's offline-world/licenses folder.

Local changes to the engine: initialize LibTomMath integers before use, include
unistd.h, save approximately every six seconds, and reopen unfinished character
design on reconnect. Native startup is exposed through a JNI entry point. Lua uses a C-locale decimal
point on Android API 19/20, where localeconv is unavailable.
The offline scripts allow joining both Shield of Arrav gangs and borrowing
Phoenix crossbows so the quest does not require a second human player.

## Saves

The offline Android app includes the user-supplied forest recording as a
low-volume, looping ambient track during play, alongside the user-supplied
background music at a slightly higher playback volume. The in-game Options tab's
Sound effects control turns effects, ambience, and music on or off. The
Sound option opens separate sliders, saved on the device. The
tracks pause when the app is backgrounded and requires no network connection.

SQLite persists position, appearance, skills, inventory, bank, and quest variables
in private app storage at `files/world-2001/rsc.sqlite` (with SQLite WAL files).
Use the in-game Logout button to finish a session. Autosaving also runs roughly
every six seconds; force-closing or OS termination can lose the most recent few
seconds. Clearing app storage or uninstalling removes the local save.
Immutable bundled assets never replace the save database. The offline package is
`org.scape2003.mudclient.offline`, separate from the online app.

## Build and verification

From org.scape2003.mudclient, run `./gradlew assembleOfflineDebug`.
Requires Java 17, SDK/build-tools 34, NDK 25.2.9519653, CMake 3.22.1.
Output: app/build/outputs/apk/offline/debug/app-offline-debug.apk.
A deliberately public debug-only keystore is included so subsequent debug APKs
can update this app without uninstalling and losing saves. It is not a release key.
The workflow verifies signatures and alignment, exercises encrypted sessions,
character creation, movement, inventory, persistence and reconnection against the
host engine, and runs the Android app on an emulator with Wi-Fi/data disabled.
Screenshots and logcat are retained as CI artifacts.

For host engine tests: `cmake -S offline -B /tmp/sundae-build`,
`cmake --build /tmp/sundae-build -j4`, then
`python3 offline/tests/smoke.py /tmp/sundae-build/sundae`.
