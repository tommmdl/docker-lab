#!/usr/bin/env python3
"""Integration and lifecycle checks; run only against this local lab."""
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get('API_BASE_URL', 'http://127.0.0.1:8000')
checks = []


def compose(*args):
    subprocess.run(['bash', 'scripts/compose.sh', *args], cwd=ROOT, check=True)


def call(path, method='GET', body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={'Content-Type': 'application/json'})
    try:
        response = urllib.request.urlopen(req, timeout=8)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read()
        return response.status, json.loads(raw) if raw else None


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)
    print('PASS: ' + name, flush=True)


def wait_ready():
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            if call('/readyz')[0] == 200:
                return
        except (OSError, ValueError):
            pass
        time.sleep(1)
    raise RuntimeError('API readiness timeout')


wait_ready()
with urllib.request.urlopen(BASE + '/', timeout=8) as response:
    html = response.read().decode()
    check('web page served with Portuguese and English strings', response.status == 200 and 'Persistent notes.' in html and 'Notas persistentes.' in html)
check('liveness returns 200', call('/healthz')[0] == 200)
check('readiness verifies database and schema', call('/readyz')[0] == 200)
for body in [{}, {'title': ''}, {'title': ' '}, {'title': 123}, [], {'title': 'a' * 201}]:
    check('rejects invalid title: ' + repr(body)[:60], call('/notes', 'POST', body)[0] == 400)
check('rejects oversized request', call('/notes', 'POST', {'title': 'a' * 5000})[0] == 413)
check('unknown route returns JSON 404', call('/missing')[0] == 404)

marker = 'persistence-' + uuid.uuid4().hex
status, note = call('/notes', 'POST', {'title': marker})
check('create returns 201 and ID', status == 201 and isinstance(note.get('id'), int))
note_id = note['id']
try:
    status, result = call('/notes')
    check('created note is readable', status == 200 and any(n['id'] == note_id for n in result['notes']))
    payload = "'); DROP TABLE notes; --"
    status, injection = call('/notes', 'POST', {'title': payload})
    check('SQL-like input stored as literal data', status == 201 and injection['title'] == payload)
    check('delete SQL-like test note', call('/notes/' + str(injection['id']), 'DELETE')[0] == 204)
    check('table remains readable', call('/notes')[0] == 200)

    compose('down')
    compose('up', '-d', '--wait', '--wait-timeout', '120')
    wait_ready()
    status, result = call('/notes')
    check('data survives container recreation', status == 200 and any(n['id'] == note_id and n['title'] == marker for n in result['notes']))

    compose('stop', 'db')
    try:
        check('liveness remains 200 during DB outage', call('/healthz')[0] == 200)
        check('readiness returns 503 during DB outage', call('/readyz')[0] == 503)
        check('data endpoint returns 503 during DB outage', call('/notes')[0] == 503)
    finally:
        compose('up', '-d', 'db')
    wait_ready()
    check('API recovers without restart', call('/notes')[0] == 200)
finally:
    wait_ready()
    check('delete persistence test note', call('/notes/' + str(note_id), 'DELETE')[0] == 204)
check('delete missing note returns 404', call('/notes/' + str(note_id), 'DELETE')[0] == 404)
result = {'executed_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
          'passed': len(checks), 'checks': checks,
          'scope': 'Local Docker lab; lifecycle tests recreate containers and stop the database.'}
output = ROOT / '.local/integration-results.json'
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2), flush=True)
