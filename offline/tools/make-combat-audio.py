"""Build the offline sound archive with a quiet synthesized hit grunt.

Uses the existing combat impact and a deterministic, vowel-like synthesized tone;
no external audio or network access is needed.
"""
import audioop
import bz2
import math
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[2]
original = root / 'org.scape2003.mudclient/app/src/main/assets/sounds1.mem'
target = root / 'org.scape2003.mudclient/app/src/offline/assets/sounds1.mem'
raw = original.read_bytes()
size = int.from_bytes(raw[:3], 'big')
archive = bz2.decompress(b'BZh1' + raw[6:]) if size != int.from_bytes(raw[3:6], 'big') else raw[6:]
count = int.from_bytes(archive[:2], 'big')

def name_hash(name):
    value = 0
    for char in name.upper():
        value = (value * 61 + ord(char) - 32) & 0xffffffff
    return value

entries = []
pos = 2 + count * 10
impact = None
for i in range(count):
    entry = archive[2+i*10:12+i*10]
    length = int.from_bytes(entry[7:10], 'big')
    data = archive[pos:pos+length]
    entries.append((entry, data))
    if int.from_bytes(entry[:4], 'big') == name_hash('combat1b.pcm'):
        assert int.from_bytes(entry[4:7], 'big') == length
        impact = audioop.ulaw2lin(data, 2)
    pos += length
assert impact is not None
# 8 kHz mono: mix the impact with a soft, short falling-pitch vocal-like tone.
rate, duration = 8000, 0.35
samples = []
for i in range(int(rate * duration)):
    t = i / rate
    onset = max(0.0, t - 0.045)
    envelope = min(1.0, onset / 0.035) * math.exp(-onset * 9.5) if t >= 0.045 else 0.0
    phase = 2 * math.pi * (150 * onset - 25 * onset * onset)
    voice = sum(math.sin(phase * h) * w for h, w in ((1, 1), (2, .45), (3, .24), (4, .15)))
    base = struct.unpack_from('<h', impact, i*2)[0] if i*2 < len(impact) else 0
    samples.append(max(-32768, min(32767, round(base + 2600 * envelope * voice))))
encoded = audioop.lin2ulaw(struct.pack('<%dh' % len(samples), *samples), 2)
header = name_hash('combathit.pcm').to_bytes(4, 'big') + len(encoded).to_bytes(3, 'big') * 2
entries.append((header, encoded))
output = len(entries).to_bytes(2, 'big') + b''.join(e for e, _ in entries) + b''.join(d for _, d in entries)
compressed = bz2.compress(output, compresslevel=1)[4:]
target.write_bytes(len(output).to_bytes(3, 'big') + len(compressed).to_bytes(3, 'big') + compressed)
print('Built offline combat sound archive:', target)
