import asyncio, json, urllib.request, sys
sys.path.insert(0, '/c/Users/kevin/AppData/Local/hermes/hermes-agent/venv/Lib/site-packages')
import websockets

# Get current page WS URL dynamically
resp = urllib.request.urlopen('http://127.0.0.1:9222/json')
data = json.loads(resp.read())
ws_url = None
page_id = None
for tab in data:
    if tab.get('type') == 'page' and 'poppop85' in tab.get('url', ''):
        ws_url = tab.get('webSocketDebuggerUrl')
        page_id = tab.get('id')
        print(f"Found page: {tab['url']}")
        break

if not ws_url:
    print("ERROR: No poppop85 page found")
    sys.exit(1)

print(f"WS URL: {ws_url}")
print(f"Page ID: {page_id}")

async def run_cdp_tests(ws_url, page_id):
    async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
        msg_id = 0
        
        async def send_cmd(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cmd = {"id": msg_id, "method": method}
            if params:
                cmd["params"] = params
            await ws.send(json.dumps(cmd))
            for _ in range(50):
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
        
        # Enable all domains
        await send_cmd("Runtime.enable")
        await send_cmd("Page.enable")
        await send_cmd("DOM.enable")
        await send_cmd("Network.enable")
        await send_cmd("Log.enable")
        await send_cmd("Runtime.enable")
        
        # Navigate fresh and wait for load complete
        nav_result = await send_cmd("Page.navigate", {"url": "https://poppop85.github.io/gesture-learning-prototype/"})
        
        # Wait for load event
        print("Waiting for frame stopped loading...")
        try:
            for _ in range(100):
                resp_data = await asyncio.wait_for(ws.recv(), timeout=2)
                r = json.loads(resp_data)
                if r.get('method') == 'Page.frameStoppedLoading':
                    print("Frame stopped loading!")
                    break
                if r.get('method') == 'Runtime.exceptionThrown':
                    ext = r.get('params', {}).get('exceptionDetails', {})
                    print(f"  JS Exception: {ext.get('exception', {}).get('details', {}).get('value', ext.get('text', 'unknown'))}")
        except asyncio.TimeoutError:
            print("Timeout waiting for load — continuing anyway")
        
        await asyncio.sleep(3)
        
        print("\n=== Checking JS execution ===")
        title = await eval_js("document.title")
        print(f"  Title: {title}")
        
        root_html = await eval_js("document.getElementById('root').innerHTML")
        print(f"  Root HTML (first 500 chars): {root_html[:500] if root_html else 'EMPTY'}")
        
        root_len = await eval_js("document.getElementById('root').children.length")
        print(f"  Root children count: {root_len}")
        
        # Check if the script was loaded
        scripts = await eval_js("""
            Array.from(document.querySelectorAll('script')).map(s => ({src: s.src, type: s.type, loaded: s.complete || true}))
        """)
        print(f"  Scripts: {scripts}")
        
        # Check for JS errors
        print("\n=== Checking console logs ===")
        # Try to get console logs
        runtime_logs = await send_cmd("Runtime.getLoggingChannels", {})
        print(f"  Log channels: {runtime_logs}")
        
        # Check if JS is actually working
        js_works = await eval_js("1 + 1")
        print(f"  JS eval works: {js_works}")
        
        # Check if React rendered
        body_children = await eval_js("Array.from(document.body.children).map(c => c.tagName + '#' + (c.id || ''))")
        print(f"  Body children: {body_children}")
        
        # Check for error in console
        console_msgs = await send_cmd("Log.getLog", {})
        print(f"  Console log: {console_msgs}")

asyncio.run(run_cdp_tests(ws_url, page_id))
