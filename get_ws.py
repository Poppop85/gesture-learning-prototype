import json, urllib.request

resp = urllib.request.urlopen('http://127.0.0.1:9222/json')
data = json.loads(resp.read())
for tab in data:
    if tab.get('type') == 'page' and 'poppop85' in tab.get('url', ''):
        print(f"WS: {tab.get('webSocketDebuggerUrl')}")
        print(f"URL: {tab['url']}")
        print(f"ID: {tab['id']}")
