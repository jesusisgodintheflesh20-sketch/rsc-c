"""Convert the original 2001 text tables to this client's binary config format.
The server continues using the untouched original archive. Only renderer texture
names are borrowed from the existing visual pack; game definitions stay 2001.
"""
import bz2, csv, io, pathlib, re, struct
ROOT=pathlib.Path(__file__).resolve().parents[2]
ASSETS=ROOT/'org.scape2003.mudclient/app/src/offline/assets'
def namehash(name):
    h=0
    for c in name.upper(): h=(h*61+ord(c)-32)&0xffffffff
    return h
def readjag(path):
    b=path.read_bytes();u=int.from_bytes(b[:3],'big');c=int.from_bytes(b[3:6],'big')
    b=bz2.decompress(b'BZh1'+b[6:]) if c!=u else b[6:]
    n=int.from_bytes(b[:2],'big');pos=2+n*10;out={}
    for i in range(n):
        row=b[2+i*10:12+i*10];h=int.from_bytes(row[:4],'big');u=int.from_bytes(row[4:7],'big');c=int.from_bytes(row[7:10],'big')
        data=b[pos:pos+c];pos+=c
        out[h]=bz2.decompress(b'BZh1'+data) if u!=c else data
    return out
legacy=readjag(ASSETS/'offline-world/config46.jag')
def table(name,lines):
    text=legacy[namehash(name+'.txt')].decode('latin1')
    rows=[next(csv.reader([row.strip().rstrip(';').rstrip(',').replace('\r',' ').replace('\n',' ')])) for row in text.split('=')[1:]]
    count=int(rows.pop(0)[0]);assert len(rows)>=count*lines,(name,count,len(rows))
    return [rows[i*lines:(i+1)*lines] for i in range(count)]
items=table('objects',4);npcs=table('npc',7);entities=table('entity',2)
locs=table('location',2);bounds=table('boundary',2);roofs=table('roof',1)
floors=table('floor',1);spells=table('spells',2);prayers=table('prayers',1)
entity_ids={v[0][0].lower():i for i,v in enumerate(entities)}
item_ids={alias.lower():i for i,v in enumerate(items) for alias in v[0][1:1+int(v[0][0])]}
# Read the texture name table from the compatible, already bundled art pack.
modern=readjag(ROOT/'cache/config85.jag');ints=modern[namehash('integer.dat')];strings=modern[namehash('string.dat')];ip=sp=0
def number(n):
    global ip
    v=int.from_bytes(ints[ip:ip+n],'big');ip+=n;return v
def string():
    global sp
    end=strings.index(0,sp);v=strings[sp:end].decode('latin1');sp=end+1;return v
n=number(2)
for _ in range(3*n):string()
ip+=n*(2+4+1+1+2+4+1+1)
n=number(2)
for _ in range(3*n):string() # names, descriptions and commands (string offsets independent)
ip+=n*(5+12+16+4+3)
n=number(2);texture_names=[string() for _ in range(n)];texture_subtypes=[string() for _ in range(n)]
textures=list(zip(texture_names,texture_subtypes))
I=bytearray();S=bytearray()
def emit(kind,value):
    if kind=='s':
        S.extend(('' if value=='_' else str(value)).encode('latin1')+b'\0');return
    value=int(value)
    if kind==4 and value<0:value=99999999-value
    I.extend((value&((1<<(8*kind))-1)).to_bytes(kind,'big'))
def columns(rows,specs):
    emit(2,len(rows))
    for kind,fn in specs:
        for row in rows:emit(kind,fn(row))
def names(v):return v[0][1]
def desc(v):return v[0][1+int(v[0][0])]
columns(items,[('s',names),('s',desc),('s',lambda v:v[1][3]),(2,lambda v:v[1][0]),(2,lambda v:v[1][1]),(1,lambda v:int(v[1][2])!=0),(1,lambda v:0),(2,lambda v:v[3][0]),(4,lambda v:int(v[3][2],16))])
# NPC sprite arrays are interleaved; other fields are columnar.
emit(2,len(npcs))
for fn in [names,desc]:
    for v in npcs:emit('s',fn(v))
for j in [0,2,3,1]:
    for v in npcs:emit(1,v[1][j])
for v in npcs:emit(1,int(v[1][0])>0)
for v in npcs:
    assert len(v[3])==12
    for name in v[3]:emit(1,entity_ids.get(name.lower(),255))
for j in range(4):
    for v in npcs:emit(4,int(v[4][j],16))
for j in range(5):
    for v in npcs:emit(2 if j<2 else 1,v[5][j])
columns(textures,[('s',lambda v:v[0]),('s',lambda v:v[1])])
columns(entities,[('s',lambda v:v[0][1]),(4,lambda v:int(v[1][0],16)),(1,lambda v:v[1][1]),(1,lambda v:v[1][2]),(1,lambda v:v[1][3]),(1,lambda v:0)])
columns(locs,[('s',names),('s',desc),('s',lambda v:v[1][5]),('s',lambda v:v[1][6]),('s',lambda v:v[1][0]),(1,lambda v:v[1][1]),(1,lambda v:v[1][2]),(1,lambda v:v[1][3]),(1,lambda v:v[1][7])])
columns(bounds,[('s',names),('s',desc),('s',lambda v:v[1][6]),('s',lambda v:v[1][7]),(2,lambda v:v[1][0]),(4,lambda v:v[1][1]),(4,lambda v:v[1][2]),(1,lambda v:v[1][3]),(1,lambda v:v[1][5])])
columns(roofs,[(1,lambda v:v[0][2]),(1,lambda v:v[0][3])])
columns(floors,[(4,lambda v:v[0][1]),(1,lambda v:v[0][2]),(1,lambda v:v[0][3])])
emit(2,2) # Two original projectile sprite sheets (magic and ranged).
emit(2,len(spells))
for j in [0,2]:
    for v in spells:emit('s',v[0][j])
for fn in [lambda v:v[0][1],lambda v:v[1][0],lambda v:v[0][3]]:
    for v in spells:emit(1,fn(v))
for v in spells:
    count=int(v[1][0]);emit(1,count)
    for k in range(count):emit(2,item_ids[v[1][1+k*2].lower()])
for v in spells:
    count=int(v[1][0]);emit(1,count)
    for k in range(count):emit(1,v[1][2+k*2])
columns(prayers,[('s',lambda v:v[0][0]),('s',lambda v:v[0][2]),(1,lambda v:v[0][1]),(1,lambda v:v[0][3])])
entries=[('string.dat',S),('integer.dat',I)]
body=len(entries).to_bytes(2,'big')
for name,data in entries:body+=struct.pack('>I',namehash(name))+len(data).to_bytes(3,'big')*2
body+=b''.join(data for _,data in entries)
result=len(body).to_bytes(3,'big')*2+body
(ASSETS/'config46.jag').write_bytes(result)
print('Converted client config:',len(items),'items,',len(npcs),'NPCs,',len(locs),'objects,',len(entities),'animations,',len(textures),'textures')
