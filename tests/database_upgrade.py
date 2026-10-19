#!/usr/bin/env python3
"""Upgrade a disposable legacy database with three notes; preserve data and login."""
import json,os,socket,subprocess,time,urllib.request,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
project='notes-upgrade-test-'+uuid.uuid4().hex[:10]
with socket.socket() as sock:
    sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
env=dict(os.environ,COMPOSE_PROJECT_NAME=project,API_PORT=str(port),API_BASE_URL=f'http://127.0.0.1:{port}')
folder=ROOT/'.local'/project;folder.mkdir(parents=True)
original='ghcr.io/tommmdl/docker-lab@sha256:3150abf7b42612192bce29be02c49880eb17f0f97c93b5527a58ae7454e97dec'
override=folder/'original.json';override.write_text(json.dumps({'services':{'db':{'image':original}}}))
def compose(*args):
    return subprocess.check_output(['bash','scripts/compose.sh','-p',project,*args],cwd=ROOT,env=env,text=True)
def call(path,body=None):
    data=None if body is None else json.dumps(body).encode()
    request=urllib.request.Request(env['API_BASE_URL']+path,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=10) as response:return json.load(response)
def volume():
    c=compose('ps','-q','db').strip()
    d=json.loads(subprocess.check_output(['docker','inspect',c],text=True))[0]
    return next(m['Name'] for m in d['Mounts'] if m['Destination']=='/var/lib/postgresql/data')
try:
    compose('-f','compose.yaml','-f',str(override),'up','-d','--no-build','--wait','--wait-timeout','180')
    assert compose('exec','-T','db','psql','-U','lab','-d','notes','-Atc',"SELECT rolsuper FROM pg_roles WHERE rolname='lab'").strip()=='t'
    for title in ['Nota em português','English note','Upgrade preserves these rows']:
        call('/notes',{'title':title})
    before=call('/notes')['notes'];assert len(before)==3
    old_volume=volume()
    compose('up','-d','--no-build','--wait','--wait-timeout','180','db')
    # Hold an old superuser session after the image restart, before role migration.
    probe="import time,psycopg; from database import connect; c=connect(); print('READY',flush=True);\nfor i in range(30):\n time.sleep(0.2)\n try:c.execute('SELECT 1')\n except psycopg.OperationalError:print('TERMINATED',flush=True);break\nelse:raise RuntimeError('Old bootstrap session stayed connected')"
    process=subprocess.Popen(['bash','scripts/compose.sh','-p',project,'exec','-T','api','python','-u','-c',probe],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert process.stdout.readline().strip()=='READY'
    compose('exec','-T','--user','postgres','db','lab-db-harden')
    output,error=process.communicate(timeout=15)
    assert process.returncode==0 and 'TERMINATED' in output,error
    subprocess.run(['python3','tests/database_security.py'],cwd=ROOT,env=env,check=True,stdout=subprocess.DEVNULL)
    after=call('/notes')['notes'];assert before==after
    assert volume()==old_volume
    result={'source_image':original,'target_image':'docker-lab-postgres:local','seeded_rows':3,'same_volume':True,'all_note_fields_preserved':before==after,'application_login_preserved':True,'application_role_was_superuser_before':True,'application_role_is_superuser_after':False,'repeated_hardening_passed':True,'old_bootstrap_session_terminated':True,'security_checks_passed':json.loads((ROOT/'.local/database-security-results.json').read_text())['checks_passed'],'scope':'Disposable legacy database upgraded in place, including bootstrap-role separation and identity sequence ownership. Test containers and volume are removed.'}
    (ROOT/'.local/database-upgrade-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
finally:
    compose('down','-v','--remove-orphans')
