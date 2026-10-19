#!/usr/bin/env python3
"""Validate both Alpine API variants on unique, disposable Compose volumes."""
import json,os,socket,subprocess,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
reports=[]
for variant,default in [('basic','docker-lab-api-alpine:local'),('traced','docker-lab-api-alpine-otel:local')]:
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 project='notes-api-alpine-'+variant+'-'+uuid.uuid4().hex[:8]
 env=dict(os.environ,COMPOSE_PROJECT_NAME=project,COMPOSE_FILE=str(ROOT/'compose.yaml')+os.pathsep+str(ROOT/'compose.api-alpine.yaml'),API_PORT=str(port),API_BASE_URL=f'http://127.0.0.1:{port}',API_ALPINE_IMAGE=os.environ.get('API_ALPINE_IMAGE' if variant=='basic' else 'API_ALPINE_OTEL_IMAGE',default),DB_EXPECTED_UID='70')
 def compose(*args):return subprocess.check_output(['bash','scripts/compose.sh',*args],cwd=ROOT,env=env)
 try:
  compose('up','-d','--no-build','--wait','--wait-timeout','180')
  for script in ['database_security.py','integration.py']:subprocess.run(['python3','tests/'+script],cwd=ROOT,env=env,check=True,stdout=subprocess.DEVNULL)
  # Both the psycopg extension and bundled libpq must work on musl.
  info=json.loads(compose('exec','-T','api','python','-c',"import json,platform,psycopg;from psycopg import pq;from database import connect;\nwith connect() as c:version=c.execute('SHOW server_version').fetchone()[0]\nprint(json.dumps({'python':platform.python_version(),'psycopg':psycopg.__version__,'pq_backend':pq.__impl__,'libpq_version':pq.version(),'postgres':version}))"))
  assert info['pq_backend']=='binary'
  result={'variant':variant,'image':env['API_ALPINE_IMAGE'],'api_checks':json.loads((ROOT/'.local/integration-results.json').read_text())['passed'],'database_security_checks':json.loads((ROOT/'.local/database-security-results.json').read_text())['checks_passed'],'runtime':info,'isolated_project':True,'original_volumes_reused':False}
  reports.append(result)
  (ROOT/'.local'/('api-alpine-'+variant+'-api-tests.json')).write_bytes((ROOT/'.local/integration-results.json').read_bytes())
  (ROOT/'.local'/('api-alpine-'+variant+'-database-tests.json')).write_bytes((ROOT/'.local/database-security-results.json').read_bytes())
 finally:compose('down','-v','--remove-orphans')
(ROOT/'.local/api-alpine-results.json').write_text(json.dumps({'variants':reports,'scope':'Two unique temporary projects/volumes; only these resources are removed. OTLP tracing is verified separately.'},indent=2)+'\n')
print(json.dumps(reports,indent=2))
