import pathlib, runpy, subprocess, tempfile
root=pathlib.Path(__file__).resolve().parents[2]
tables=runpy.run_path(str(root/'offline/tools/client_config.py'))
with tempfile.TemporaryDirectory() as d:
    d=pathlib.Path(d)
    for name in ['string.dat','integer.dat']:
        data=tables['readjag'](tables['ASSETS']/'config46.jag')[tables['namehash'](name)]
        (d/name).write_bytes(data)
    subprocess.run(['cc','-std=gnu99','-DSDL2','-DRENDER_SW','-I'+str(root/'org.scape2003.mudclient/app/jni/SDL/include'),str(root/'src/game-data.c'),str(root/'offline/tests/client-config.c'),'-o',str(d/'test')],check=True)
    subprocess.run([str(d/'test'),str(d)],check=True)

# All legacy creatures and world objects must have renderable assets.
hashname=tables['namehash']
free=tables['readjag'](root/'cache/entity24.jag')
member=tables['readjag'](root/'cache/entity24.mem')
for v in tables['entities']:
    for suffix,used in [('',True),('a',int(v[1][2])),('f',int(v[1][3]))]:
        name=v[0][1]+suffix+'.dat'
        assert not used or hashname(name) in free or hashname(name) in member, name
models=tables['readjag'](root/'cache/models36.jag')
for v in tables['locs']:
    name=v[1][0]+'.ob3'
    assert v[1][0].lower()=='na' or hashname(name) in models, name
print('PASS: all legacy character frames and world models are bundled')
