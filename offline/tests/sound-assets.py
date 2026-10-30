"""Ensure each cue emitted by the offline world is present in the sound archive."""
import bz2
from pathlib import Path
p = Path(__file__).resolve().parents[2] / 'org.scape2003.mudclient/app/src/main/assets/sounds1.mem'
b = p.read_bytes()
size, packed = int.from_bytes(b[:3], 'big'), int.from_bytes(b[3:6], 'big')
b = bz2.decompress(b'BZh1' + b[6:]) if size != packed else b[6:]
count = int.from_bytes(b[:2], 'big')
hashes = {int.from_bytes(b[2 + 10*i:6 + 10*i], 'big') for i in range(count)}
def name_hash(s):
    h = 0
    for c in s.upper(): h = (h * 61 + ord(c) - 32) & 0xffffffff
    return h
for name in ('combat1a', 'combat1b', 'death', 'advance', 'mine', 'fish', 'cooking', 'prayeron', 'prayeroff'):
    assert name_hash(name + '.pcm') in hashes, name
print('PASS: all offline sound cues exist in the bundled archive')
