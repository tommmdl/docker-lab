#!/usr/bin/env python3
"""Safe privilege and residual XML checks, using this lab's Compose project."""
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def compose(*args):
    return subprocess.check_output(['bash','scripts/compose.sh',*args],cwd=ROOT,text=True)
# Repeat the migration to verify it also works on an existing database.
compose('exec','-T','--user','postgres','db','lab-db-harden')
compose('exec','-T','--user','postgres','db','lab-db-harden')
code=r'''
import json,os,urllib.request
import psycopg
from database import connect
checks=[]
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
def forbidden(sql):
    with connect() as c:
        try:c.execute(sql)
        except psycopg.errors.InsufficientPrivilege:return True
        return False
with connect() as c:
    row=c.execute("SELECT rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname=current_user").fetchone()
    check('Application role has no superuser, database/role creation, replication or RLS-bypass flags',row==tuple([False]*5))
    check('Bootstrap superuser is separate from the application',c.execute("SELECT rolname FROM pg_roles WHERE oid=10").fetchone()[0]=='notes_bootstrap')
    settings=c.execute("SELECT rolconfig FROM pg_roles WHERE rolname=current_user").fetchone()[0]
    check('Default statement timeout is 5 seconds',c.execute('SHOW statement_timeout').fetchone()[0]=='5s' and 'statement_timeout=5s' in settings)
    check('Idle transaction timeout is 10 seconds',c.execute('SHOW idle_in_transaction_session_timeout').fetchone()[0]=='10s' and 'idle_in_transaction_session_timeout=10s' in settings)
    check('Benign SQL XML parsing is available',c.execute("SELECT XMLPARSE(DOCUMENT '<root/>' )::text").fetchone()[0]=='<root/>')
check('Application cannot become the maintenance role',forbidden('SET ROLE notes_admin'))
check('Application cannot become the bootstrap superuser',forbidden('SET ROLE notes_bootstrap'))
check('Application cannot read server files',forbidden("SELECT pg_read_file('/etc/hostname')"))
check('Application cannot execute server-side commands',forbidden("COPY (SELECT 1) TO PROGRAM 'true'"))
check('Application cannot create roles',forbidden('CREATE ROLE lab_forbidden_role_probe'))
for role in ['notes_admin','notes_bootstrap']:
    try:
        with psycopg.connect(host=os.environ['DB_HOST'],dbname='notes',user=role,password='not-a-secret',connect_timeout=3):pass
    except psycopg.OperationalError as error:
        check('Administrative role '+role+' is explicitly rejected over TCP','pg_hba.conf rejects connection' in str(error))
    else:raise AssertionError('Administrative role accepted a TCP connection')
with connect() as c:
    try:c.execute('SELECT pg_sleep(6)')
    except psycopg.errors.QueryCanceled:check('Long query is cancelled',True)
    else:raise AssertionError('Long query was not cancelled')
body=json.dumps({'title':'<root>&unknown;</root>'}).encode()
request=urllib.request.Request('http://127.0.0.1:8000/notes',data=body,headers={'Content-Type':'application/json'})
with urllib.request.urlopen(request,timeout=8) as response:
    note=json.load(response);check('XML-looking title stays literal text through the API',response.status==201 and note['title']=='<root>&unknown;</root>')
request=urllib.request.Request('http://127.0.0.1:8000/notes/'+str(note['id']),method='DELETE')
with urllib.request.urlopen(request,timeout=8) as response:check('Security test note is deleted',response.status==204)
print(json.dumps({'checks_passed':len(checks),'checks':checks,'xml_parser_reachable':True}))
'''
result=json.loads(compose('exec','-T','api','python','-c',code))
container=compose('ps','-q','db').strip()
state=json.loads(subprocess.check_output(['docker','inspect',container],text=True))[0]
for name,condition in [
 ('Database memory is limited to 384 MiB',state['HostConfig']['Memory']==384*1024*1024),
 ('Database CPU is limited to one core',state['HostConfig']['NanoCpus']==1000000000),
 ('Database PID count is limited to 256',state['HostConfig']['PidsLimit']==256),
 ('Database does not publish a host port',not state['HostConfig']['PortBindings']),
 ('Database main process runs as expected non-root UID',compose('exec','-T','db','sh','-c',"awk '/^Uid:/{print $2}' /proc/1/status").strip()==os.environ.get('DB_EXPECTED_UID','999') and os.environ.get('DB_EXPECTED_UID','999')!='0'),
]:
    if not condition:raise AssertionError(name)
    result['checks'].append(name)
result['checks_passed']=len(result['checks'])
result['scope']='Privilege boundaries and resource limits; benign XML reachability, not a CVE exploit or patch verification.'
(ROOT/'.local/database-security-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
