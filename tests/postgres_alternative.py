#!/usr/bin/env python3
"""Logical migration and rollback checks on separate Debian/Alpine volumes."""
import json,os,socket,subprocess,urllib.request,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
uid=uuid.uuid4().hex[:10]
folder=ROOT/'.local'/('postgres-alternative-'+uid);folder.mkdir(parents=True)
baseline='ghcr.io/tommmdl/docker-lab@sha256:be42c09595d7059956490eeab607b742afc96268db48f91f4eb1fd53edc89b52'
override=folder/'source.json';override.write_text(json.dumps({'services':{'db':{'image':baseline,'environment':{'POSTGRES_INITDB_ARGS':'--encoding=UTF8 --locale=en_US.utf8'}},'api':{'image':os.environ.get('ALTERNATIVE_API_IMAGE','docker-lab-api:local')}}}))
def free_port():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def environment(name,files,port,expected_uid):
    return dict(os.environ,COMPOSE_PROJECT_NAME=name,COMPOSE_FILE=os.pathsep.join(map(str,files)),API_PORT=str(port),API_BASE_URL=f'http://127.0.0.1:{port}',DB_EXPECTED_UID=expected_uid)
source=environment('notes-alt-source-'+uid,[ROOT/'compose.yaml',override],free_port(),'999')
target=environment('notes-alt-target-'+uid,[ROOT/'compose.yaml',ROOT/'compose.postgres-alpine.yaml'],int(os.environ.get('ALTERNATIVE_API_PORT','0')) or free_port(),'70')
target['POSTGRES_ALTERNATIVE_IMAGE']=os.environ.get('POSTGRES_ALTERNATIVE_IMAGE','docker-lab-postgres-alpine:local')
target['ALTERNATIVE_API_IMAGE']=os.environ.get('ALTERNATIVE_API_IMAGE','docker-lab-api:local')
checks=[]
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
def compose(env,*args,data=None):
    return subprocess.check_output(['bash','scripts/compose.sh',*args],cwd=ROOT,env=env,input=data)
def sql(env,query,db='notes',user='lab'):
    return compose(env,'exec','-T','db','psql','-U',user,'-d',db,'-Atc',query).decode().strip()
def call(env,path,body=None,method=None):
    payload=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request(env['API_BASE_URL']+path,data=payload,method=method,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=10) as response:return json.load(response) if response.status!=204 else None
def rows(env,db='notes'):
    return sql(env,"SELECT coalesce(json_agg(n ORDER BY id),'[]'::json) FROM (SELECT id,title,created_at FROM notes) n",db)
def sequence(env,db='notes'):
    return sql(env,'SELECT last_value,is_called FROM notes_id_seq',db)
def locale(env):
    return json.loads(sql(env,"SELECT row_to_json(d) FROM (SELECT datlocprovider,datcollate,datctype,datlocale,datcollversion FROM pg_database WHERE datname=current_database()) d"))
def volume(env):
    cid=compose(env,'ps','-q','db').decode().strip()
    d=json.loads(subprocess.check_output(['docker','inspect',cid]))[0]
    return next(x['Name'] for x in d['Mounts'] if x['Destination']=='/var/lib/postgresql/data')
def dump(env,db='notes'):
    return compose(env,'exec','-T','db','pg_dump','-U','notes_admin','-d',db,'--format=custom','--no-owner','--no-acl')
def restore(env,data,db='notes'):
    compose(env,'exec','-T','db','pg_restore','-U','lab','-d',db,'--no-owner','--no-acl','--exit-on-error','--single-transaction',data=data)
keep=os.environ.get('KEEP_ALTERNATIVE')=='1'
success=False
try:
    compose(source,'up','-d','--no-build','--wait','--wait-timeout','180')
    fixtures=['Ação e automação','English note','São Paulo – café','日本語のメモ','Emoji 🚀',"O'Reilly & <xml>literal</xml>",'e\u0301 and é']
    for title in fixtures:call(source,'/notes',{'title':title})
    original_rows=rows(source);original_sequence=sequence(source);original_api=call(source,'/notes')
    check('Source contains seven Unicode notes',len(original_api['notes'])==7)
    backup=dump(source);(folder/'notes.dump').write_bytes(backup)
    compose(target,'up','-d','--no-build','--wait','--wait-timeout','180','db')
    check('Source and target use separate volumes',volume(source)!=volume(target))
    restore(target,backup)
    check('Logical restore preserves every note field',rows(target)==original_rows)
    check('Identity sequence state is preserved at restore',sequence(target)==original_sequence)
    check('Target uses UTF8',sql(target,'SHOW server_encoding')=='UTF8')
    check('Target uses PostgreSQL 17',sql(target,'SHOW server_version_num').startswith('17'))
    schema="SELECT column_name,data_type,is_nullable,is_identity FROM information_schema.columns WHERE table_schema='public' AND table_name='notes' ORDER BY ordinal_position"
    check('Column types, nullability and identity are preserved',sql(source,schema)==sql(target,schema))
    indexes="SELECT indexdef FROM pg_indexes WHERE schemaname='public' AND tablename='notes' ORDER BY indexname"
    check('Notes indexes are preserved',sql(source,indexes)==sql(target,indexes))
    source_locale=locale(source);target_locale=locale(target)
    check('Target locale provider is explicitly ICU/en-US',target_locale['datlocprovider']=='i' and target_locale['datlocale']=='en-US')
    compose(target,'up','-d','--no-build','--wait','--wait-timeout','180')
    check('API returns the same restored notes',call(target,'/notes')==original_api)
    note=call(target,'/notes',{'title':'Identity after restore'})
    check('New generated ID does not collide',note['id']>max(n['id'] for n in original_api['notes']))
    call(target,'/notes/'+str(note['id']),method='DELETE')
    for script,report in [('database_security.py','database-security-results.json'),('integration.py','integration-results.json')]:
        subprocess.run(['python3','tests/'+script],cwd=ROOT,env=target,check=True,stdout=subprocess.DEVNULL)
        (folder/report).write_bytes((ROOT/'.local'/report).read_bytes())
    check('Restored notes survive all API and lifecycle checks',rows(target)==original_rows)
    check('Benign XPath works with the replacement libxml2',sql(target,"SELECT xpath('/root/text()', XMLPARSE(DOCUMENT '<root>ok</root>'))::text")=='{ok}')
    compose(source,'exec','-T','db','createdb','-U','notes_admin','-O','lab','roundtrip_check')
    restore(source,dump(target),'roundtrip_check')
    check('Logical rollback into a separate Debian database preserves every row',rows(source,'roundtrip_check')==rows(target))
    check('Logical rollback preserves current sequence state',sequence(source,'roundtrip_check')==sequence(target))
    check('Original source rows remain unchanged',rows(source)==original_rows)
    check('Original source sequence remains unchanged',sequence(source)==original_sequence)
    live_results=[]
    if os.environ.get('ALTERNATIVE_LIVE_MANIFEST'):
        for entry in json.loads(Path(os.environ['ALTERNATIVE_LIVE_MANIFEST']).read_text()):
            name=entry['name'];dbname='restore_'+name
            assert name in ['kubernetes','compose','demo']
            compose(target,'exec','-T','db','createdb','-U','notes_admin','-O','lab',dbname)
            restore(target,Path(entry['dump']).read_bytes(),dbname)
            # Actual note content remains private; publish only match results and counts.
            expected=json.loads(Path(entry['rows']).read_text())
            actual=json.loads(rows(target,dbname));check('Live '+name+' backup restores without changing note fields',actual==expected)
            live_results.append({'source':name,'rows':len(actual),'all_note_fields_preserved':actual==expected})
    result={'checks_passed':len(checks),'checks':checks,'source_image':baseline,'candidate_image':target.get('POSTGRES_ALTERNATIVE_IMAGE','docker-lab-postgres-alpine:local'),'source_locale':source_locale,'target_locale':target_locale,'source_volume_reused':False,'fixture_rows':7,'api_checks':json.loads((folder/'integration-results.json').read_text())['passed'],'security_checks':json.loads((folder/'database-security-results.json').read_text())['checks_passed'],'live_restores':live_results,'scope':'Separate volumes and logical dumps; lab notes schema, not a physical data-directory swap or a general PostgreSQL migration certification.'}
    (ROOT/'.local/postgres-alternative-results.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'.local/postgres-alternative-api-tests.json').write_bytes((folder/'integration-results.json').read_bytes())
    (ROOT/'.local/postgres-alternative-security-tests.json').write_bytes((folder/'database-security-results.json').read_bytes())
    if keep:
        state={'project':target['COMPOSE_PROJECT_NAME'],'compose_file':target['COMPOSE_FILE'],'api_port':target['API_PORT'],'url':target['API_BASE_URL'],'scope':'Isolated alternative with seven fixture notes; original environments unchanged.'}
        (ROOT/'.local/postgres-alternative-state.json').write_text(json.dumps(state,indent=2)+'\n')
    success=True
    print(json.dumps(result,indent=2))
finally:
    compose(source,'down','-v','--remove-orphans')
    if not (keep and success):compose(target,'down','-v','--remove-orphans')
