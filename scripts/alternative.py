#!/usr/bin/env python3
"""Operate only the isolated alternative; down preserves its volume."""
import json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
state_file=root/'.local/postgres-alternative-state.json'
state=json.loads(state_file.read_text()) if state_file.exists() else {'project':'notes-postgres-alternative','api_port':'8015'}
project=state['project']
if not (project=='notes-postgres-alternative' or project.startswith('notes-alt-target-')):raise SystemExit('Refusing a project outside the alternative lab')
env=dict(os.environ,COMPOSE_PROJECT_NAME=project,COMPOSE_FILE=str(root/'compose.yaml')+os.pathsep+str(root/'compose.postgres-alpine.yaml'),API_PORT=state['api_port'])
base=['bash','scripts/compose.sh']
command=sys.argv[1] if len(sys.argv)>1 else 'status'
if command in ['up','test']:
    images=subprocess.check_output(base+['config','--images'],cwd=root,env=env,text=True).splitlines()
    for reference in images:
        if subprocess.run(['docker','image','inspect',reference],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
            subprocess.run(['docker','pull',reference],check=True)
    if command=='test':
        config=json.loads(subprocess.check_output(base+['config','--format','json'],cwd=root,env=env,text=True))
        env.update(ALTERNATIVE_API_IMAGE=config['services']['api']['image'],POSTGRES_ALTERNATIVE_IMAGE=config['services']['db']['image'])
        raise SystemExit(subprocess.call(['python3','tests/postgres_alternative.py'],cwd=root,env=env))
    state.update({'compose_file':env['COMPOSE_FILE'],'url':'http://127.0.0.1:'+state['api_port'],'scope':'Isolated alternative; down preserves its own volume.'})
    state_file.parent.mkdir(exist_ok=True);state_file.write_text(json.dumps(state,indent=2)+'\n')
    args=['up','-d','--no-build','--wait','--wait-timeout','180']
elif command=='status':args=['ps']
elif command=='logs':args=['logs','--no-color','--tail=50']
elif command=='down':args=['down']
else:raise SystemExit('Usage: bash scripts/alternative.sh {up|test|status|logs|down}')
raise SystemExit(subprocess.call(base+args,cwd=root,env=env))
