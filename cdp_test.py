import asyncio, json, urllib.request, sys
sys.path.insert(0, '/c/Users/kevin/AppData/Local/hermes/hermes-agent/venv/Lib/site-packages')
import websockets

# Get current page WS URL dynamically
resp = urllib.request.urlopen('http://127.0.0.1:9222/json')
data = json.loads(resp.read())
ws_url = None
for tab in data:
    if tab.get('type') == 'page' and 'poppop85' in tab.get('url', ''):
        ws_url = tab.get('webSocketDebuggerUrl')
        print(f"Found page: {tab['url']}")
        break

if not ws_url:
    print("ERROR: No poppop85 page found")
    sys.exit(1)

print(f"WS URL: {ws_url}")

async def run_cdp_tests(ws_url):
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
        
        # Enable domains
        await send_cmd("Runtime.enable")
        await send_cmd("Page.enable")
        await send_cmd("DOM.enable")
        
        # Navigate fresh
        await send_cmd("Page.navigate", {"url": "https://poppop85.github.io/gesture-learning-prototype/"})
        
        print("\nWaiting for page to load (10s)...")
        await asyncio.sleep(10)
        
        print("\n=== STEP 1: Verify dashboard ===")
        title = await eval_js("document.title")
        print(f"  Page title: {title}")
        
        root_len = await eval_js("document.getElementById('root').innerHTML.length")
        print(f"  Root content length: {root_len}")
        
        has_dashboard = await eval_js("document.querySelector('.dashboard') !== null")
        print(f"  Dashboard present: {has_dashboard}")
        
        has_fb = await eval_js("document.getElementById('ut-feedback-toggle') !== null")
        print(f"  Feedback widget present: {has_fb}")
        
        if root_len == 0:
            print("  Root is empty — waiting more (5s)...")
            await asyncio.sleep(5)
            root_len = await eval_js("document.getElementById('root').innerHTML.length")
            print(f"  Root content length now: {root_len}")
        
        lesson_titles = await eval_js("Array.from(document.querySelectorAll('.lesson-card h4')).map(el => el.textContent.trim())")
        print(f"  Lesson titles: {lesson_titles}")
        
        header_stats = await eval_js("Array.from(document.querySelectorAll('.header-stats .stat-item')).map(el => el.textContent.trim())")
        print(f"  Header stats: {header_stats}")
        
        # Check for errors in console
        console_errors = await eval_js("""
            // Check if any error elements exist
            document.querySelector('.error') !== null;
        """)
        print(f"  Error elements: {console_errors}")
        
        print("\n=== STEP 2: Start hiragana lesson ===")
        result = await eval_js("""
            const cards = document.querySelectorAll('.lesson-card');
            if (cards.length > 0) { cards[0].click(); return 'clicked lesson: ' + cards[0].querySelector('h4').textContent.trim(); }
            return 'no cards found';
        """)
        print(f"  {result}")
        
        await asyncio.sleep(1)
        
        has_intro = await eval_js("document.querySelector('.intro-card') !== null")
        print(f"  Intro card present: {has_intro}")
        
        if has_intro:
            intro_title = await eval_js("document.querySelector('.intro-card h2') ? document.querySelector('.intro-card h2').textContent.trim() : 'no title'")
            print(f"  Intro title: {intro_title}")
            
            elements_list = await eval_js("""
                Array.from(document.querySelectorAll('.elements-preview li')).map(li => li.textContent.trim())
            """)
            print(f"  Elements preview: {elements_list}")
            
            start_btn = await eval_js("""
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Start Learning'));
                btn ? btn.textContent.trim() : 'not found';
            """)
            print(f"  Start button: {start_btn}")
            
            if start_btn != 'not found':
                result = await eval_js("""
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Start Learning'));
                    btn.click();
                    'clicked Start Learning';
                """)
                print(f"  {result}")
                await asyncio.sleep(1)
        
        print("\n=== STEP 3: Teach card ===")
        has_teach = await eval_js("document.querySelector('.teach-card') !== null")
        print(f"  Teach card present: {has_teach}")
        
        if has_teach:
            kana = await eval_js("document.querySelector('.kana') ? document.querySelector('.kana').textContent.trim() : 'no kana'")
            print(f"  Kana: {kana}")
            
            romaji = await eval_js("document.querySelector('.romaji') ? document.querySelector('.romaji').textContent.trim() : 'no romaji'")
            print(f"  Romaji: {romaji}")
            
            english = await eval_js("document.querySelector('.english') ? document.querySelector('.english').textContent.trim() : 'no english'")
            print(f"  English: {english}")
            
            gesture_name = await eval_js("document.querySelector('.gesture-demo h4') ? document.querySelector('.gesture-demo h4').textContent.trim() : 'no gesture demo'")
            print(f"  Gesture demo: {gesture_name}")
            
            memory_anchor = await eval_js("document.querySelector('.gesture-memory-anchor') ? document.querySelector('.gesture-memory-anchor').textContent.trim() : 'no anchor'")
            print(f"  Memory anchor: {memory_anchor}")
            
            cultural_note = await eval_js("document.querySelector('.cultural-note') ? document.querySelector('.cultural-note').textContent.trim() : 'no cultural note'")
            print(f"  Cultural note: {cultural_note}")
            
            gesture_btn = await eval_js("""
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Watch Gesture') || b.textContent.includes('Stop Demo'));
                btn ? btn.textContent.trim() : 'no button';
            """)
            print(f"  Gesture button: {gesture_btn}")
            
            # Start demo
            result = await eval_js("""
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Watch Gesture'));
                if (btn) { btn.click(); return 'started demo'; }
                return 'no Watch button';
            """)
            print(f"  {result}")
            await asyncio.sleep(2)
            
            has_feedback = await eval_js("document.querySelector('.feedback-overlay') !== null")
            print(f"  Feedback overlay present: {has_feedback}")
            
            feedback_state = await eval_js("document.querySelector('.feedback-state') ? document.querySelector('.feedback-state').textContent.trim() : 'no state'")
            print(f"  Feedback state: {feedback_state}")
            
            feedback_msg = await eval_js("document.querySelector('.feedback-message') ? document.querySelector('.feedback-message').textContent.trim() : 'no msg'")
            print(f"  Feedback message: {feedback_msg}")
            
            intensity = await eval_js("document.querySelector('.feedback-intensity .intensity-bar') ? document.querySelector('.feedback-intensity .intensity-bar').style.width : 'no bar'")
            print(f"  Intensity bar: {intensity}")
            
            # Stop demo
            await asyncio.sleep(1)
            result = await eval_js("""
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Stop Demo'));
                if (btn) { btn.click(); return 'stopped demo'; }
                return 'no Stop button';
            """)
            print(f"  {result}")
            
            await asyncio.sleep(1)
            
            # Go to practice
            result = await eval_js("""
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Practice Gesture') || b.textContent.includes('Continue to Practice'));
                if (btn) { btn.click(); return 'went to practice'; }
                return 'no practice button';
            """)
            print(f"  {result}")
            await asyncio.sleep(1)
        
        print("\n=== STEP 4: Practice card ===")
        has_practice = await eval_js("document.querySelector('.practice-card') !== null")
        print(f"  Practice card present: {has_practice}")
        
        if has_practice:
            # Mirror gesture
            result = await eval_js("""
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Mirror the Gesture'));
                if (btn) { btn.click(); return 'mirrored gesture'; }
                return 'no mirror button';
            """)
            print(f"  {result}")
            
            await asyncio.sleep(3)
            
            fb_banner = await eval_js("document.querySelector('.feedback-banner') ? document.querySelector('.feedback-banner').textContent.trim() : 'no feedback banner'")
            print(f"  Feedback banner: {fb_banner}")
            
            fb_banner_class = await eval_js("document.querySelector('.feedback-banner') ? document.querySelector('.feedback-banner').className : 'no banner'")
            print(f"  Feedback banner class: {fb_banner_class}")
            
            quiz_section = await eval_js("""
                const quiz = document.querySelector('.quiz-section');
                if (quiz) {
                    const q = quiz.querySelector('h4') ? quiz.querySelector('h4').textContent.trim() : '';
                    const p = quiz.querySelector('p') ? quiz.querySelector('p').textContent.trim() : '';
                    const input = quiz.querySelector('input') ? quiz.querySelector('input').placeholder : 'no input';
                    return q + ' | ' + p + ' | input: ' + input;
                }
                return 'no quiz section';
            """)
            print(f"  Quiz section: {quiz_section}")
            
            # Submit quiz
            result = await eval_js("""
                const input = document.querySelector('.quiz-form input');
                if (input) {
                    input.value = 'a';
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    const submit = document.querySelector('.quiz-form button');
                    if (submit) { submit.click(); return 'submitted: a'; }
                    return 'no submit button';
                }
                return 'no quiz input';
            """)
            print(f"  Quiz submit: {result}")
            
            await asyncio.sleep(1)
            quiz_result = await eval_js("document.querySelector('.quiz-result') ? document.querySelector('.quiz-result').textContent.trim() : 'no result'")
            print(f"  Quiz result: {quiz_result}")
            
            practice_btns = await eval_js("Array.from(document.querySelectorAll('.practice-actions button')).map(b => b.textContent.trim())")
            print(f"  Practice buttons: {practice_btns}")
            
            # Skip to quiz
            result = await eval_js("""
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Skip Quiz'));
                if (btn) { btn.click(); return 'went to quiz'; }
                return 'no Skip Quiz button';
            """)
            print(f"  {result}")
            await asyncio.sleep(1)
        
        print("\n=== STEP 5: Quiz card ===")
        has_quiz = await eval_js("document.querySelector('.quiz-card') !== null")
        print(f"  Quiz card present: {has_quiz}")
        
        if has_quiz:
            quiz_q = await eval_js("document.querySelector('.quiz-question') ? document.querySelector('.quiz-question').textContent.trim() : 'no question'")
            print(f"  Quiz question: {quiz_q}")
            
            quiz_opts = await eval_js("Array.from(document.querySelectorAll('.quiz-option')).map(b => b.textContent.trim())")
            print(f"  Quiz options: {quiz_opts}")
            
            # Check duplicates
            if quiz_opts and len(quiz_opts) > 0:
                seen = set()
                dups = []
                for o in quiz_opts:
                    if o in seen: dups.append(o)
                    seen.add(o)
                print(f"  Duplicate options: {len(dups) > 0} ({dups})")
            else:
                print(f"  No quiz options found!")
            
            # Select first option
            await asyncio.sleep(0.5)
            result = await eval_js("""
                const btn = document.querySelector('.quiz-option');
                if (btn) { btn.click(); return 'selected: ' + btn.textContent.trim(); }
                return 'no option';
            """)
            print(f"  {result}")
            
            await asyncio.sleep(1)
            quiz_reveal = await eval_js("document.querySelector('.quiz-answer-reveal') ? document.querySelector('.quiz-answer-reveal').textContent.trim().substring(0, 200) : 'no reveal'")
            print(f"  Quiz reveal: {quiz_reveal}")
            
            # Next/complete
            result = await eval_js("""
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Next') || b.textContent.includes('Continue'));
                if (btn) { btn.click(); return 'clicked: ' + btn.textContent.trim(); }
                return 'no next button';
            """)
            print(f"  {result}")
            await asyncio.sleep(1)
        
        print("\n=== STEP 6: Review card ===")
        has_review = await eval_js("document.querySelector('.review-card') !== null")
        print(f"  Review card present: {has_review}")
        
        if has_review:
            review_info = await eval_js("""
                const rc = document.querySelector('.review-card');
                const h2 = rc.querySelector('h2') ? rc.querySelector('h2').textContent.trim() : '';
                const reward = rc.querySelector('.reward-xp') ? rc.querySelector('.reward-xp').textContent.trim() : '';
                const badge = rc.querySelector('.reward-badge') ? rc.querySelector('.reward-badge').textContent.trim() : '';
                const stats = rc.querySelector('.review-stats') ? rc.querySelector('.review-stats').textContent.trim() : '';
                return h2 + ' | ' + reward + ' | ' + badge + ' | ' + stats;
            """)
            print(f"  Review: {review_info}")
            
            review_btns = await eval_js("Array.from(document.querySelectorAll('.review-actions button')).map(b => b.textContent.trim())")
            print(f"  Review buttons: {review_btns}")
            
            # Go back to dashboard
            result = await eval_js("""
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Back to Lessons'));
                if (btn) { btn.click(); return 'went back to dashboard'; }
                return 'no back button';
            """)
            print(f"  {result}")
            await asyncio.sleep(1)
        
        print("\n=== STEP 7: Check for audio ===")
        has_audio = await eval_js("""
            document.querySelector('audio') !== null || 
            Array.from(document.querySelectorAll('button')).some(b => b.textContent.includes('▶') || b.textContent.includes('🔊') || b.textContent.includes('🔈') || b.textContent.includes('Play'))
        """)
        print(f"  Audio playback present: {has_audio}")
        
        # Check for audioRef data
        audio_notes = await eval_js("""
            // Check if any element has audioRef field (non-null)
            Array.from(document.querySelectorAll('.teach-card, .practice-card')).map(el => 'has audio element: ' + (el.querySelector('audio') !== null)).join('; ');
        """)
        print(f"  Audio in cards: {audio_notes}")
        
        print("\n=== STEP 8: Check GestureOverlay ===")
        overlay_present = await eval_js("document.querySelector('.gesture-overlay') !== null")
        print(f"  GestureOverlay on page: {overlay_present}")
        
        overlay_state = await eval_js("document.querySelector('.gesture-overlay') ? document.querySelector('.gesture-overlay').textContent.trim().substring(0, 100) : 'no overlay'")
        print(f"  Overlay content: {overlay_state}")
        
        print("\n=== STEP 9: Full page text ===")
        all_text = await eval_js("""
            Array.from(document.querySelectorAll('button, h1, h2, h3, h4, p, span'))
                .map(el => el.textContent.trim())
                .filter(t => t.length > 3 && t.length < 200)
                .filter((t, i, arr) => arr.indexOf(t) === i)
                .slice(0, 80)
                .join('\\n');
        """)
        print(f"  {all_text}")
        
        print("\n=== STEP 10: Navigate through all elements ===")
        # Start phrases lesson
        result = await eval_js("""
            const cards = Array.from(document.querySelectorAll('.lesson-card'));
            const phrasesCard = cards.find(c => c.querySelector('h4').textContent.includes('Daily Phrases'));
            if (phrasesCard) { phrasesCard.click(); return 'clicked Phrases'; }
            if (cards.length > 1) { cards[1].click(); return 'clicked card[1]'; }
            return 'no card found';
        """)
        print(f"  {result}")
        
        await asyncio.sleep(1)
        
        # Click Start Learning
        result = await eval_js("""
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Start Learning'));
            if (btn) { btn.click(); return 'started'; }
            return 'not found';
        """)
        print(f"  {result}")
        
        await asyncio.sleep(1)
        
        # Check teach card for phrases lesson
        teach_info = await eval_js("""
            const tc = document.querySelector('.teach-card');
            if (tc) {
                const kana = tc.querySelector('.kana') ? tc.querySelector('.kana').textContent.trim() : '';
                const romaji = tc.querySelector('.romaji') ? tc.querySelector('.romaji').textContent.trim() : '';
                const gesture = tc.querySelector('.gesture-demo h4') ? tc.querySelector('.gesture-demo h4').textContent.trim() : '';
                return kana + ' | ' + romaji + ' | gesture: ' + gesture;
            }
            return 'no teach card';
        """)
        print(f"  Teach info: {teach_info}")
        
        # Watch gesture demo
        result = await eval_js("""
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Watch Gesture'));
            if (btn) { btn.click(); return 'demo started'; }
            return 'no watch button';
        """)
        print(f"  {result}")
        await asyncio.sleep(2)
        
        # Check feedback overlay during demo
        feedback_text = await eval_js("""
            const overlay = document.querySelector('.feedback-overlay');
            if (overlay) {
                return overlay.textContent.trim().replace(/\\s+/g, ' ').substring(0, 200);
            }
            return 'no feedback overlay';
        """)
        print(f"  Feedback overlay: {feedback_text}")
        
        # Stop demo
        result = await eval_js("""
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Stop Demo'));
            if (btn) { btn.click(); return 'stopped'; }
            return 'no stop button';
        """)
        print(f"  {result}")
        
        await asyncio.sleep(1)
        
        # Practice
        result = await eval_js("""
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Practice Gesture'));
            if (btn) { btn.click(); return 'went to practice'; }
            return 'not found';
        """)
        print(f"  {result}")
        
        await asyncio.sleep(1)
        
        # Mirror gesture and check feedback
        result = await eval_js("""
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Mirror the Gesture'));
            if (btn) { btn.click(); return 'mirrored'; }
            return 'no mirror button';
        """)
        print(f"  {result}")
        
        await asyncio.sleep(3)
        
        # Check all feedback banners
        fb_banners = await eval_js("""
            Array.from(document.querySelectorAll('.feedback-banner')).map(el => ({class: el.className, text: el.textContent.trim()})).slice(-3);
        """)
        print(f"  Feedback banners (last 3): {fb_banners}")
        
        # Check quiz and answer
        result = await eval_js("""
            const input = document.querySelector('.quiz-form input');
            if (input) {
                input.value = 'k';
                input.dispatchEvent(new Event('input', { bubbles: true }));
                const submit = document.querySelector('.quiz-form button');
                if (submit) { submit.click(); return 'submitted: k'; }
            }
            return 'not found';
        """)
        print(f"  Quiz submit: {result}")
        await asyncio.sleep(1)
        
        quiz_result = await eval_js("document.querySelector('.quiz-result') ? document.querySelector('.quiz-result').textContent.trim() : 'no result'")
        print(f"  Quiz result: {quiz_result}")
        
        # Skip to quiz
        result = await eval_js("""
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Skip Quiz'));
            if (btn) { btn.click(); return 'quiz'; }
            return 'not found';
        """)
        print(f"  {result}")
        await asyncio.sleep(1)
        
        # Quiz card
        quiz_opts = await eval_js("Array.from(document.querySelectorAll('.quiz-option')).map(b => b.textContent.trim())")
        print(f"  Quiz options: {quiz_opts}")
        if quiz_opts:
            seen = set(); dups = [o for o in quiz_opts if o in seen or seen.add(o)]
            print(f"  Duplicates: {dups}")
        
        # Select correct answer
        result = await eval_js("""
            const btn = document.querySelector('.quiz-option');
            if (btn) { btn.click(); return 'selected: ' + btn.textContent.trim(); }
            return 'no option';
        """)
        print(f"  Quiz select: {result}")
        await asyncio.sleep(1)
        
        reveal = await eval_js("document.querySelector('.quiz-answer-reveal') ? document.querySelector('.quiz-answer-reveal').textContent.trim().substring(0, 200) : 'no reveal'")
        print(f"  Reveal: {reveal}")
        
        # Complete lesson
        result = await eval_js("""
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Next'));
            if (btn) { btn.click(); return 'next clicked'; }
            return 'no next';
        """)
        print(f"  {result}")
        await asyncio.sleep(1)
        
        has_review = await eval_js("document.querySelector('.review-card') !== null")
        print(f"  Review card: {has_review}")
        
        if has_review:
            milestone_text = await eval_js("document.querySelector('.review-card').textContent.trim().replace(/\\s+/g, ' ').substring(0, 300)")
            print(f"  Review content: {milestone_text}")
        
        print("\n=== ALL STEPS COMPLETE ===")
        
        # Final: get console messages
        print("\n=== Checking for JS console errors ===")
        # We can't easily get console logs via CDP eval, but let's check for error elements
        error_check = await eval_js("""
            // Look for any error/disabled states
            {
                buttons: Array.from(document.querySelectorAll('button')).map(b => ({text: b.textContent.trim(), disabled: b.disabled, visible: b.offsetParent !== null})).filter(b => b.visible),
                errorElements: document.querySelectorAll('.error, .text-red, .error-message').length,
                allText: document.body.textContent.trim().replace(/\\s+/g, ' ').substring(0, 500)
            };
        """)
        print(f"  Error elements: {error_check.get('errorElements')}")
        visible_buttons = error_check.get('buttons', [])
        print(f"  Visible buttons ({len(visible_buttons)}):")
        for btn in visible_buttons:
            print(f"    - '{btn.get('text', '')}' (disabled={btn.get('disabled')})")

asyncio.run(run_cdp_tests(ws_url))
