# User Test Plan — Te de Nihongo Gesture Learning Prototype

**Date:** 2026-08-19
**Target:** 5-10 beginner Japanese learners (0-3 months study experience)
**Duration:** 15-20 minutes per session
**Live URL:** https://poppop85.github.io/gesture-learning-prototype/

## Test Environment

The prototype runs in any modern browser (Chrome, Firefox, Safari, Edge). No installation required. Gesture recognition uses a **mock API** that simulates hand detection — users interact with simulated gesture demos and feedback. The full flow from dashboard → teach → practice → quiz → review is functional.

## Test Protocol

### Session Structure (15-20 min)

1. **Intro (2 min)** — Briefly explain the concept: learning Japanese phrases through memorable hand gestures
2. **Task Walkthrough (10-12 min)** — User completes a full lesson flow:
   - Select a lesson from the dashboard
   - Watch gesture demo on the Teach card
   - Try "Mirror the Gesture" in Practice
   - Answer the quick quiz
   - Complete the retrieval quiz
   - Review milestone rewards
3. **Feedback (5 min)** — Collect structured feedback

## Tasks to Assign

Users should complete these tasks without assistance:

1. Start any lesson and navigate through the full flow
2. Watch a gesture demonstration and observe the feedback
3. Answer a practice quiz question
4. Complete a retrieval quiz
5. Observe the level/XP/streak system
6. Find and interact with the badge gallery

## Feedback Questions

### Gesture Detection Accuracy (simulated)
1. How clear was the gesture feedback during the demo? (1-5 scale)
2. Did the gesture state transitions (acquiring → recognized → confirmed) feel natural? (1-5)
3. Were you able to understand what each gesture represented? (1-5)

### Learning Effectiveness
4. Did the gesture memory anchors help you remember the phrase/meaning? (1-5, open comment)
5. Was the progression from teach → practice → quiz logical? (1-5)
6. How would you rate the quiz difficulty? (Too easy / Just right / Too hard)

### User Engagement
7. How engaging did you find the overall experience? (1-5)
8. Did the gamification elements (XP, badges, streaks) motivate you? (1-5)
9. What frustrated you or felt confusing? (open text)
10. What did you like most? (open text)

### Interface & Navigation
11. Was navigation between phases intuitive? (1-5)
12. Any elements that felt broken or not working? (open text)
13. Device/browser used? (mobile/desktop, OS)

## Feedback Collection

Users can submit feedback via:
- GitHub Issues: https://github.com/Poppop85/gesture-learning-prototype/issues/new
- Direct message to @Poppop85 on LINE

## Scoring Rubric

| Score | Label | Action |
|-------|-------|--------|
| 4-5 | Positive | Monitor, no action needed |
| 3 | Neutral | Investigate, minor improvement |
| 1-2 | Negative | **High priority fix** |

## Priority Fix Criteria

Feedback items are prioritized by:
1. **Blocker severity** — prevents task completion
2. **Frequency** — percentage of users who reported it
3. **Impact on learning** — affects comprehension or retention
4. **Ease of fix** — effort required to address
