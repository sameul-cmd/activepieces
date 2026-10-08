"""Phase 0 helper: drive a local Activepieces CE stack through its REST API (stdlib only).

Usage (from repo root, stack in explore/stack, token in explore/stack/.token):
  python3 -I docs/exploration/ap_api.py import <flow.json> [--enable]
  python3 -I docs/exploration/ap_api.py webhook <flowId> '<json body>' [--sync]
  python3 -I docs/exploration/ap_api.py runs [limit]
  python3 -I docs/exploration/ap_api.py run <runId>
flow.json = {"displayName": ..., "trigger": {...}} (same shape as a template's flows[0]).
"""
import json
import pathlib
import sys
import urllib.error
import urllib.request

BASE = 'http://localhost:8080/api/v1'
TOKEN = pathlib.Path('explore/stack/.token').read_text().strip()


def call(method, path, body=None, auth=True):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header('content-type', 'application/json')
    if auth:
        req.add_header('authorization', f'Bearer {TOKEN}')
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip().startswith(('{', '[')) else raw)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:2000]


def project_id():
    return pathlib.Path('explore/stack/.project').read_text().strip()


def import_flow(path, enable):
    spec = json.loads(pathlib.Path(path).read_text())
    status, flow = call('POST', '/flows', {'displayName': spec['displayName'], 'projectId': project_id()})
    assert status in (200, 201), (status, flow)
    fid = flow['id']
    op = {'type': 'IMPORT_FLOW', 'request': {'displayName': spec['displayName'], 'trigger': spec['trigger'], 'schemaVersion': spec.get('schemaVersion'), 'notes': []}}
    status, res = call('POST', f'/flows/{fid}', op)
    print('import', status, '' if status == 200 else res)
    if enable:
        status, res = call('POST', f'/flows/{fid}', {'type': 'LOCK_AND_PUBLISH', 'request': {}})
        print('publish', status, '' if status == 200 else res)
        status, res = call('POST', f'/flows/{fid}', {'type': 'CHANGE_STATUS', 'request': {'status': 'ENABLED'}})
        print('enable', status, '' if status == 200 else res)
    print('flowId', fid)


def main():
    cmd = sys.argv[1]
    if cmd == 'import':
        import_flow(sys.argv[2], '--enable' in sys.argv)
    elif cmd == 'webhook':
        suffix = '/sync' if '--sync' in sys.argv else ''
        print(call('POST', f'/webhooks/{sys.argv[2]}{suffix}', json.loads(sys.argv[3]), auth=False))
    elif cmd == 'runs':
        limit = sys.argv[2] if len(sys.argv) > 2 else '10'
        status, res = call('GET', f'/flow-runs?projectId={project_id()}&limit={limit}')
        for r in res['data']:
            print(r['id'], r['status'], r.get('flowVersion', {}).get('displayName') or r.get('flowDisplayName'), r['created'])
    elif cmd == 'run':
        print(json.dumps(call('GET', f'/flow-runs/{sys.argv[2]}')[1], indent=1)[:6000])


if __name__ == '__main__':
    main()
