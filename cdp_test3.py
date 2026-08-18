import asyncio, json, urllib.request, sys
sys.path.insert(0, '/c/Users/kevin/AppData/Local/hermes/hermes-agent/venv/Lib/site-packages')
import websockets

resp = urllib.request.urlopen('http://127.0.0.1:9222/json')
data = json.loads(resp.read())
ws_url = None
for tab in data:
    if tab.get('type') == 'page' and 'poppop85' in tab.get('url', ''):
        ws_url = tab.get('webSocketDebuggerUrl')
        break

async def run(ws_url):
    async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
        msg_id = 0
        
        async def send_cmd(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cmd = {"id": msg_id, "method": method}
            if params:
                cmd["params"] = params
            await ws.send(json.dumps(cmd))
            for _ in range(100):
                try:
                    resp_data = await asyncio.wait_for(ws.recv(), timeout=5)
                    r = json.loads(resp_data)
                    if r.get('id') == msg_id:
                        return r
                except asyncio.TimeoutError:
                    pass
            return {}
        
        async def eval_js(expr):
            result = await send_cmd("Runtime.evaluate", {"expression": expr})
            return result.get('result', {}).get('result', {}).get('value', None)
        
        await send_cmd("Runtime.enable")
        await send_cmd("Page.enable")
        await send_cmd("Network.enable")
        
        # Collect all events for 3 seconds
        print("Navigating and collecting events...")
        await send_cmd("Page.navigate", {"url": "https://poppop85.github.io/gesture-learning-prototype/"})
        
        events = []
        try:
            while True:
                resp_data = await asyncio.wait_for(ws.recv(), timeout=1)
                r = json.loads(resp_data)
                if r.get('method'):
                    events.append(r)
                elif r.get('id'):
                    if r.get('id') == msg_id:
                        pass
        except asyncio.TimeoutError:
            pass
        
        await asyncio.sleep(3)
        
        # Get more events
        try:
            while True:
                resp_data = await asyncio.wait_for(ws.recv(), timeout=1)
                r = json.loads(resp_data)
                if r.get('method'):
                    events.append(r)
        except asyncio.TimeoutError:
            pass
        
        # Print interesting events
        print("\n=== Network Events ===")
        for e in events:
            method = e.get('method', '')
            if method.startswith('Network.'):
                params = e.get('params', {})
                if 'response' in params:
                    resp_data = params['response']
                    print(f"  {method}: {resp_data.get('url','?')} -> status={resp_data.get('status','?')}")
                elif 'request' in params:
                    req = params['request']
                    print(f"  {method}: {req.get('url','')} method={req.get('method','')}")
        
        print("\n=== Runtime Events ===")
        for e in events:
            method = e.get('method', '')
            if method.startswith('Runtime.'):
                params = e.get('params', {})
                if 'exceptionDetails' in params:
                    ext = params['exceptionDetails']
                    exc = ext.get('exception', {})
                    details = exc.get('details', {})
                    print(f"  Exception: {ext.get('text','')} | {details.get('value','').get('description','')[:200] if details.get('value') else ''}")
                elif 'entry' in params:
                    entry = params['entry']
                    print(f"  Console: level={entry.get('level')} text={entry.get('text','')[:200]}")
        
        print("\n=== Page Events ===")
        for e in events:
            method = e.get('method', '')
            if method.startswith('Page.'):
                print(f"  {method}: {json.dumps(e.get('params', {}))[:200]}")
        
        # Check root
        root = await eval_js("document.getElementById('root').innerHTML")
        print(f"\n=== Root HTML length: {len(root) if root else 0} ===")
        if root and len(root) > 0:
            print(f"Root HTML: {root[:500]}")
        
        # Check script tags
        scripts = await eval_js("""
            Array.from(document.scripts).map(s => s.src + ' | type=' + s.type + ' | loaded=' + (s.complete || false))
        """)
        print(f"Scripts: {scripts}")
        
        # Check if feedback.js is present
        has_feedback = await eval_js("typeof initFeedbackWidget !== 'undefined' || document.getElementById('ut-feedback-toggle') !== null")
        print(f"Feedback widget initialized: {has_feedback}")

asyncio.run(run(ws_url))
