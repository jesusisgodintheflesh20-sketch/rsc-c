"""Exercise the real encrypted client protocol against the embedded engine."""
import ctypes as C
import atexit, pathlib, shutil, socket, sqlite3, struct, subprocess, sys, tempfile, time
root = pathlib.Path(__file__).resolve().parents[1]
if pathlib.Path(sys.argv[1]).is_file():
    temporary = tempfile.TemporaryDirectory()
    atexit.register(temporary.cleanup)
    world = pathlib.Path(temporary.name)/'world'
    assets = root.parent/'org.scape2003.mudclient/app/src/offline/assets/offline-world'
    shutil.copytree(assets,world)
    logfile = open(pathlib.Path(temporary.name)/'server.log','w')
    process = subprocess.Popen([str(pathlib.Path(sys.argv[1]).resolve()),'-b',str(world),'-f',str(world/'settings.ini')],stdout=logfile,stderr=subprocess.STDOUT)
    def stop():
        process.terminate()
        process.wait(timeout=10)
    atexit.register(stop)
    for _ in range(100):
        if process.poll() is not None:
            logfile.flush()
            raise RuntimeError((pathlib.Path(temporary.name)/'server.log').read_text())
        try:
            socket.create_connection(('127.0.0.1',43595),timeout=.1).close()
            time.sleep(1)
            break
        except OSError: time.sleep(.1)
else:
    world = pathlib.Path(sys.argv[1])
libpath = '/tmp/offline-isaac.so'
subprocess.run(['cc','-shared','-fPIC',str(root/'vendor/src/ext/isaac.c'),'-o',libpath],check=True)
class Isaac(C.Structure):
    _fields_ = [('rsl', C.c_uint32*256),('cnt',C.c_uint32),('mm',C.c_uint32*256),('aa',C.c_uint32),('bb',C.c_uint32),('cc',C.c_uint32)]
lib = C.CDLL(libpath)
lib.isaac_next.restype = C.c_uint32

def frame(body):
    n=len(body)
    return (bytes([n,body[-1]])+body[:-1]) if n<160 else bytes([160+n//256,n%256])+body

def receive(s,n):
    b=b''
    while len(b)<n:
        p=s.recv(n-len(b))
        assert p, 'Disconnected'
        b+=p
    return b

def login():
    s=socket.create_connection(('127.0.0.1',43595),timeout=10)
    first=receive(s,4)
    s.sendall(frame(bytes([32,0])))
    session=first+receive(s,4)
    keys=[12345,67890,*struct.unpack('>II',session)]
    # Client pads both fields to 20 characters, then appends a newline.
    block=b'\x0a'+struct.pack('>4II',*keys,0)+b'Adventurer'.ljust(20)+b'\n'+b'offlineworld'.ljust(20)+b'\n'
    exponent=int('10001',16)
    modulus=int('bafe89212f1d00b87648328e6e78853255c7dd5837e2883bb704b1f63c1e42a28109d0be1a9dfd71c8a260e8ec5a97e70ec26aa6a010c4e8a83182bebfb0d993',16)
    encrypted=pow(int.from_bytes(block,'big'),exponent,modulus).to_bytes(64,'big').lstrip(b'\0')
    s.sendall(frame(b'\0\0'+struct.pack('>H',203)+bytes([0,len(encrypted)])+encrypted))
    response=receive(s,1)[0]
    assert response in (0,1,25), f'Login failed: {response}'
    rng=Isaac()
    for i,k in enumerate(keys): rng.rsl[i]=k
    lib.isaac_init(C.byref(rng),1)
    return s,rng

def send(s,rng,opcode,payload=b''):
    s.sendall(frame(bytes([(opcode+lib.isaac_next(C.byref(rng)))&255])+payload))

s,rng=login()
# New characters must finish the original appearance/class selection flow.
# A network login and persisted world state prove this is a real server session.
send(s,rng,235,bytes([1,0,1,2,2,8,14,0]))
# Wait for server ticks and autosaving rather than assuming a fixed tick phase.
for attempt in range(20):
    time.sleep(.6)
    send(s,rng,187,struct.pack('>HH',120,649))
    if (world/'rsc.sqlite').exists():
        with sqlite3.connect(world/'rsc.sqlite') as db:
            saved=db.execute('select x,y,rpg_class from players').fetchone()
            if saved and saved[:2]==(120,649) and saved[2]!=255:
                break
s.settimeout(2)
world_data=s.recv(65536)
assert len(world_data)>100, 'Expected world/inventory/NPC packets'
send(s,rng,102)
time.sleep(3)
s.close()
with sqlite3.connect(world/'rsc.sqlite') as db:
    row=db.execute('select id,x,y,login_date from players where username=?',('adventurer',)).fetchone()
    if row is None: row=db.execute('select id,x,y,login_date from players').fetchone()
    assert row and row[3]>0, f'Player did not persist: {row}'
    assert row[1:3] == (120,649), f'Local movement failed: {row}'
    assert db.execute('select count(*) from players_inventory').fetchone()[0] > 0, 'Starter inventory missing'
s,rng=login()
time.sleep(1)
send(s,rng,102)
s.close()
print('PASS: RSA/ISAAC login, populated world packets, SQLite save, and login with existing local character',row)
