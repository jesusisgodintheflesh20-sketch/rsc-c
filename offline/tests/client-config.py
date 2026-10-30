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
