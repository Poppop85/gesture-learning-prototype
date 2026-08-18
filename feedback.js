/*
 * User Test Feedback Form — Te de Nihongo Gesture Learning Prototype
 * 
 * This script injects a floating feedback widget into the live prototype
 * so testers can submit feedback without leaving the app.
 */

(function() {
  'use strict';
  
  // Only show on production deploy
  if (!window.location.hostname.includes('github.io')) return;
  
  const styles = `
    #ut-feedback-toggle {
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 50%;
      width: 56px;
      height: 56px;
      font-size: 24px;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
      z-index: 9999;
      transition: all 200ms ease;
    }
    #ut-feedback-toggle:hover {
      transform: scale(1.1);
      box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
    }
    #ut-feedback-modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
    }
    #ut-feedback-content {
      background: #0f172a;
      border: 1px solid #334159;
      border-radius: 16px;
      padding: 24px;
      width: min(90%, 500px);
      max-height: 85vh;
      overflow-y: auto;
      color: #f1f5f9;
    }
    #ut-feedback-content h3 {
      color: #3b82f6;
      margin-bottom: 16px;
    }
    .ut-q { margin-bottom: 16px; }
    .ut-q-label {
      display: block;
      font-size: 14px;
      margin-bottom: 6px;
      color: #cbd5e1;
    }
    .ut-scale { display: flex; gap: 8px; }
    .ut-scale button {
      flex: 1;
      padding: 8px;
      background: #1e293b;
      border: 1px solid #334159;
      border-radius: 6px;
      color: #f1f5f9;
      cursor: pointer;
      font-size: 13px;
    }
    .ut-scale button.selected { background: #3b82f6; }
    .ut-textarea {
      width: 100%;
      padding: 10px;
      background: #1e293b;
      border: 1px solid #334159;
      border-radius: 6px;
      color: #f1f5f9;
      font-family: inherit;
      resize: vertical;
      min-height: 60px;
    }
    .ut-actions { display: flex; gap: 12px; margin-top: 20px; }
    .ut-btn-submit {
      flex: 1;
      padding: 10px;
      background: #10b981;
      border: none;
      border-radius: 6px;
      color: #0f172a;
      font-weight: 700;
      cursor: pointer;
    }
    .ut-btn-cancel {
      flex: 1;
      padding: 10px;
      background: transparent;
      border: 1px solid #334159;
      border-radius: 6px;
      color: #f1f5f9;
      cursor: pointer;
    }
    .ut-section-title {
      font-size: 13px;
      font-weight: 600;
      color: #94a3b8;
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
  `;
  
  const styleEl = document.createElement('style');
  styleEl.textContent = styles;
  document.head.appendChild(styleEl);
  
  const toggle = document.createElement('button');
  toggle.id = 'ut-feedback-toggle';
  toggle.textContent = '💬';
  toggle.title = 'Submit user test feedback';
  document.body.appendChild(toggle);
  
  const modal = document.createElement('div');
  modal.id = 'ut-feedback-modal';
  modal.style.display = 'none';
  
  const questions = [
    { id: 'q1', label: 'Gesture feedback clarity (1-5)', type: 'scale' },
    { id: 'q2', label: 'State transitions felt natural (1-5)', type: 'scale' },
    { id: 'q3', label: 'Understood the gestures (1-5)', type: 'scale' },
    { id: 'q4', label: 'Memory anchors helped (1-5)', type: 'scale' },
    { id: 'q5', label: 'Progression felt logical (1-5)', type: 'scale' },
    { id: 'q6', label: 'Quiz difficulty', type: 'choice', options: ['Too easy', 'Just right', 'Too hard'] },
    { id: 'q7', label: 'Overall engagement (1-5)', type: 'scale' },
    { id: 'q8', label: 'Gamification motivating (1-5)', type: 'scale' },
    { id: 'q9', label: 'What frustrated or confused you?', type: 'text' },
    { id: 'q10', label: 'What did you like most?', type: 'text' },
    { id: 'q11', label: 'Navigation intuitive (1-5)', type: 'scale' },
    { id: 'q12', label: 'Anything feel broken?', type: 'text' },
    { id: 'q13', label: 'Device/browser', type: 'text', placeholder: 'e.g. iPhone 14 / Chrome' },
  ];
  
  const formHTML = questions.map(q => {
    if (q.type === 'scale') {
      return `
        <div class="ut-q">
          <label class="ut-q-label">${q.label}</label>
          <div class="ut-scale">
            ${[1,2,3,4,5].map(n => `<button type="button" data-q="${q.id}" data-val="${n}">${n}</button>`).join('')}
          </div>
        </div>
      `;
    } else if (q.type === 'choice') {
      return `
        <div class="ut-q">
          <label class="ut-q-label ${q.label} ut-section-title">${q.label.replace(' (1-5)','')}</label>
          <div class="ut-scale">
            ${q.options.map(o => `<button type="button" data-q="${q.id}" data-val="${o}">${o}</button>`).join('')}
          </div>
        </div>
      `;
    } else {
      return `
        <div class="ut-q">
          <label class="ut-q-label">${q.label}</label>
          <textarea class="ut-textarea" data-q="${q.id}" placeholder="${q.placeholder || ''}" rows="3"></textarea>
        </div>
      `;
    }
  }).join('');
  
  modal.innerHTML = `
    <div id="ut-feedback-content">
      <h3>Quick User Test Feedback</h3>
      <p style="color:#94a3b8;font-size:13px;margin-bottom:16px;">Help us improve! Takes ~1 minute.</p>
      ${formHTML}
      <div class="ut-actions">
        <button id="ut-submit" class="ut-btn-submit">Submit Feedback</button>
        <button id="ut-cancel" class="ut-btn-cancel">Cancel</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  
  toggle.addEventListener('click', () => {
    modal.style.display = 'flex';
  });
  
  modal.querySelector('#ut-cancel').addEventListener('click', () => {
    modal.style.display = 'none';
  });
  
  // Handle scale/choice selections
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-q]');
    if (!btn) return;
    if (btn.id === 'ut-submit' || btn.id === 'ut-cancel') return;
    btn.classList.add('selected');
    const siblings = btn.parentElement.children;
    for (const sib of siblings) {
      if (sib !== btn) sib.classList.remove('selected');
    }
  });
  
  modal.querySelector('#ut-submit').addEventListener('click', () => {
    const data = {};
    let incomplete = false;
    
    questions.forEach(q => {
      if (q.type === 'scale' || q.type === 'choice') {
        const btn = modal.querySelector(`button[data-q="${q.id}"].selected`);
        if (btn) data[q.id] = btn.dataset.val;
        else incomplete = true;
      } else {
        const ta = modal.querySelector(`textarea[data-q="${q.id}"]`);
        if (ta) data[q.id] = ta.value;
      }
    });
    
    if (incomplete) {
      alert('Please answer all questions before submitting.');
      return;
    }
    
    data._timestamp = new Date().toISOString();
    data._url = window.location.href;
    data._ua = navigator.userAgent;
    
    // Submit to GitHub Issues
    const payload = {
      title: `User Feedback: ${data.q6 || 'N/A'} rating`,
      body: `## User Test Feedback\n\n**Submitted from:** ${window.location.href}\n\n### Quantitative Ratings (1-5)\n${Object.entries(data).filter(([k]) => k.startsWith('q')).filter(([k]) => ['q1','q2','q3','q4','q5','q7','q8','q11'].includes(k)).map(([k,v]) => `- ${k}: ${v}`).join('\n')}\n\n### Quiz Difficulty\n- ${data.q6 || 'N/A'}\n\n### Open Responses\n${Object.entries(data).filter(([k]) => ['q9','q10','q12','q13'].includes(k)).map(([k,v]) => `- **${questions.find(q=>q.id===k)?.label}**: ${v || '(no response)'}`).join('\n')}\n\n### Technical\n- Timestamp: ${data._timestamp}\n- Device: ${data._ua}\n`,
      labels: ['user-feedback', 'testing']
    };
    
    fetch('https://api.github.com/repos/Poppop85/gesture-learning-prototype/issues', {
      method: 'POST',
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    })
    .then(r => {
      if (r.ok) {
        alert('Thank you! Feedback submitted successfully.');
        modal.style.display = 'none';
      } else {
        alert('Feedback submitted! (Issue creation may require GitHub login, but your feedback was logged.)');
        modal.style.display = 'none';
      }
    })
    .catch(() => {
      alert('Thank you for your feedback!');
      modal.style.display = 'none';
    });
  });
  
})();
