import json, urllib.request

# Get all targets
resp = urllib.request.urlopen('http://127.0.0.1:9222/json')
data = json.loads(resp.read())
for tab in data:
    if tab.get('type') == 'page':
        print(json.dumps({'id': tab['id'], 'type': tab['type'], 'url': tab['url']}, indent=2))
        print(f"WS: {tab.get('webSocketDebuggerUrl', 'N/A')}")
