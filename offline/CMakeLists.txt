cmake_minimum_required(VERSION 3.16)
project(sundae C)
set(CMAKE_C_STANDARD 99)
file(GLOB ENGINE vendor/src/*.c vendor/src/config/*.c vendor/src/ext/libjag/lib/*.c vendor/src/protocol/opcodes*.c)
list(FILTER ENGINE EXCLUDE REGEX "loop-(kqueue|select)\\.c$")
file(GLOB LUA deps/lua/src/*.c)
list(FILTER LUA EXCLUDE REGEX "/(lua|luac)\\.c$")
file(GLOB TOM deps/tommath/*.c)
set(SOURCES ${ENGINE} ${LUA} ${TOM}
 vendor/src/protocol/incoming.c vendor/src/protocol/outgoing.c vendor/src/protocol/rsa-libtom.c
 vendor/src/persistence/database-sqlite.c vendor/src/persistence/pwhash-argon2.c
 vendor/src/ext/flea.c vendor/src/ext/isaac.c vendor/src/ext/reallocarr.c vendor/src/ext/inih/ini.c
 deps/sqlite/sqlite3.c
 deps/argon2/src/argon2.c deps/argon2/src/core.c deps/argon2/src/encoding.c deps/argon2/src/ref.c deps/argon2/src/thread.c deps/argon2/src/blake2/blake2b.c
 deps/bzip2/blocksort.c deps/bzip2/huffman.c deps/bzip2/crctable.c deps/bzip2/randtable.c deps/bzip2/compress.c deps/bzip2/decompress.c deps/bzip2/bzlib.c)
if(ANDROID)
 add_library(sundae SHARED ${SOURCES} android-jni.c)
 set_source_files_properties(vendor/src/server.c PROPERTIES COMPILE_DEFINITIONS "main=sundae_main")
 target_link_options(sundae PRIVATE -Wl,-Bsymbolic)
else()
 add_executable(sundae ${SOURCES})
endif()
target_compile_definitions(sundae PRIVATE WITH_RSA_LIBTOM ARGON2_NO_THREADS LUA_USE_POSIX SQLITE_THREADSAFE=1)
target_include_directories(sundae PRIVATE vendor/src/ext/libjag/include vendor/src/ext/inih deps/lua/src deps/tommath deps/sqlite deps/argon2/include deps/bzip2)
target_link_libraries(sundae m dl)

# LibTomMath uses constant-condition feature dispatch; dead calls must be eliminated.
target_compile_options(sundae PRIVATE -O2)
