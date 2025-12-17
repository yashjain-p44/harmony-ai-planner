# Frontend-Backend Integration Testing Checklist

## Prerequisites

- [ ] Backend server is running on `http://localhost:5000`
- [ ] Google Calendar OAuth is configured in the backend
- [ ] Frontend dependencies are installed (`npm install`)
- [ ] `.env` file exists with `VITE_API_BASE_URL=http://localhost:5000`

## Test Scenarios

### 1. Backend Connectivity Test

**Steps**:
1. Start the backend: `python app/api/app.py`
2. Open browser and navigate to `http://localhost:5000/health`
3. Verify you see: `{"status": "ok", "message": "API is running"}`

**Expected Result**: ✅ Backend is responding

---

### 2. Frontend Startup Test

**Steps**:
1. Navigate to `figma-frontend` directory
2. Run `npm run dev`
3. Open `http://localhost:5173` in browser
4. Check browser console for errors

**Expected Result**: 
- ✅ Frontend loads without errors
- ✅ No API connection errors in console
- ✅ "API Offline" warning NOT shown (if backend is running)

---

### 3. API Health Indicator Test

**Test Case 3a: Backend Online**

**Steps**:
1. Ensure backend is running
2. Load frontend
3. Check top-right corner of dashboard

**Expected Result**: ✅ No "API Offline" warning shown

**Test Case 3b: Backend Offline**

**Steps**:
1. Stop the backend server
2. Reload frontend
3. Check top-right corner of dashboard

**Expected Result**: ✅ Orange "API Offline" warning is displayed

---

### 4. AI Chatbot Integration Test

**Test Case 4a: Basic Chat**

**Steps**:
1. Click the floating AI assistant button (right side of screen)
2. AI panel slides in from the right
3. Type: "Hello"
4. Press Enter or click Send button

**Expected Result**:
- ✅ Message appears in chat
- ✅ Loading spinner shows briefly
- ✅ AI response appears
- ✅ No error messages

**Test Case 4b: Calendar Query**

**Steps**:
1. Open AI panel
2. Type: "What events do I have today?"
3. Send message

**Expected Result**:
- ✅ AI responds with calendar information
- ✅ Or explains no events found

**Test Case 4c: Task Creation**

**Steps**:
1. Open AI panel
2. Type: "Schedule a meeting tomorrow at 2pm for 1 hour"
3. Send message

**Expected Result**:
- ✅ AI acknowledges the request
- ✅ Task preview card may appear (optional based on parsing)
- ✅ AI provides confirmation or asks for clarification

**Test Case 4d: Conversation Context**

**Steps**:
1. Send first message: "I need to schedule a meeting"
2. Send follow-up: "Make it tomorrow at 3pm"
3. Send another: "For 2 hours"

**Expected Result**:
- ✅ AI maintains context across messages
- ✅ Understands references to previous messages

**Test Case 4e: Error Handling**

**Steps**:
1. Stop the backend server
2. Try sending a message in the chat

**Expected Result**:
- ✅ Error message appears in chat
- ✅ "Sorry, I had trouble connecting to the server..." message
- ✅ No app crash

---

### 5. Calendar Events Display Test

**Test Case 5a: Events Loading**

**Steps**:
1. Complete onboarding with Google Calendar connection
2. Navigate to dashboard
3. Observe calendar view

**Expected Result**:
- ✅ Calendar loads
- ✅ Google Calendar events appear
- ✅ Events have 📅 emoji/icon
- ✅ Events show in correct time slots

**Test Case 5b: Different Views**

**Steps**:
1. Click "Day" view toggle
2. Observe events in day view
3. Click "Week" view toggle
4. Observe events in week view
5. Click "Month" view toggle
6. Observe events in month view

**Expected Result**:
- ✅ Events display correctly in all views
- ✅ Date navigation works (prev/next buttons)
- ✅ Google Calendar events styled differently

**Test Case 5c: Manual Refresh**

**Steps**:
1. In dashboard, find "Refresh" button (near calendar settings)
2. Click "Refresh" button
3. Observe loading state

**Expected Result**:
- ✅ Refresh icon spins during load
- ✅ Calendar events update
- ✅ Button re-enables after loading

**Test Case 5d: Event Details**

**Steps**:
1. Click on a calendar event in any view
2. Modal/detail view should appear

**Expected Result**:
- ✅ Event details shown
- ✅ Title, time, duration displayed
- ✅ Google Calendar events marked as read-only

---

### 6. Mixed Tasks and Events Test

**Test Case 6a: Display Both**

**Steps**:
1. Ensure you have Google Calendar events
2. Create a manual task via "Add Task" button
3. Observe calendar view

**Expected Result**:
- ✅ Both manual tasks and Google events display
- ✅ Visual distinction between them
- ✅ No overlap or rendering issues

**Test Case 6b: Task vs Event Interaction**

**Steps**:
1. Click on a manual task
2. Verify you can edit/delete
3. Click on a Google Calendar event
4. Verify it's read-only

**Expected Result**:
- ✅ Manual tasks are editable
- ✅ Google events cannot be modified
- ✅ Clear visual feedback

---

### 7. Error Scenarios

**Test Case 7a: Network Error During Chat**

**Steps**:
1. Open AI panel
2. Disconnect from network (or stop backend)
3. Send a message

**Expected Result**:
- ✅ Error message in chat
- ✅ No app crash
- ✅ Can retry after reconnecting

**Test Case 7b: Invalid Calendar Response**

**Steps**:
1. Modify backend to return invalid data (optional)
2. Try refreshing calendar

**Expected Result**:
- ✅ Graceful error handling
- ✅ Console shows error (for debugging)
- ✅ User sees empty calendar or error message

---

### 8. Performance Tests

**Test Case 8a: Large Calendar Load**

**Steps**:
1. Ensure you have 50+ calendar events in next 30 days
2. Load dashboard
3. Observe loading time

**Expected Result**:
- ✅ Events load within reasonable time (< 5 seconds)
- ✅ UI remains responsive
- ✅ No lag when switching views

**Test Case 8b: Rapid Chat Messages**

**Steps**:
1. Open AI panel
2. Send multiple messages quickly (5-10 messages)

**Expected Result**:
- ✅ All messages queued properly
- ✅ Responses appear in order
- ✅ No message loss
- ✅ Send button disables during loading

---

### 9. UI/UX Tests

**Test Case 9a: Responsive Design**

**Steps**:
1. Resize browser window
2. Test at various widths (desktop, tablet, mobile)

**Expected Result**:
- ✅ Layout adjusts appropriately
- ✅ AI panel remains accessible
- ✅ Calendar view scales

**Test Case 9b: Loading States**

**Steps**:
1. Observe loading indicators throughout app
2. Check during calendar refresh
3. Check during chat message sending

**Expected Result**:
- ✅ Loading spinners shown
- ✅ Buttons disabled during loading
- ✅ Clear visual feedback

**Test Case 9c: Empty States**

**Steps**:
1. View calendar with no events
2. Open AI chat

**Expected Result**:
- ✅ Helpful empty state messages
- ✅ Suggestions for getting started
- ✅ No blank screens

---

### 10. Integration Flow Test (End-to-End)

**Complete User Journey**:

1. **Onboarding**
   - [ ] Complete onboarding flow
   - [ ] Connect Google Calendar
   - [ ] Reach dashboard

2. **Calendar Viewing**
   - [ ] See Google Calendar events
   - [ ] Navigate between views
   - [ ] Click on events for details

3. **AI Interaction**
   - [ ] Open AI panel
   - [ ] Ask about schedule: "What's on my calendar today?"
   - [ ] Create task: "Schedule focus time tomorrow morning"
   - [ ] Get AI confirmation

4. **Manual Task Creation**
   - [ ] Click "Add Task" button
   - [ ] Fill task form
   - [ ] Submit and see it in calendar

5. **Calendar Sync**
   - [ ] Click "Refresh" button
   - [ ] Verify events update
   - [ ] Add event in Google Calendar (external)
   - [ ] Refresh in app and see new event

**Expected Result**: ✅ Complete flow works without errors

---

## Known Limitations

1. **Google Calendar events are read-only** - Cannot edit/delete from frontend
2. **30-day window** - Only fetches events from next 30 days
3. **Single calendar** - Only primary calendar is synced
4. **No real-time sync** - Manual refresh required for calendar updates
5. **Task creation from chat** - May require manual confirmation

---

## Debugging Tips

### Check Backend Logs
```bash
# In backend terminal, watch for API call logs
# Look for errors, warnings, or stack traces
```

### Check Browser Console
```javascript
// Open DevTools (F12)
// Check Console tab for errors
// Check Network tab for failed API calls
```

### Verify API Calls
```bash
# Test endpoints directly
curl http://localhost:5000/health
curl http://localhost:5000/calendar/events?max_results=5
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'
```

### Check Environment Variables
```bash
# In figma-frontend directory
cat .env
# Should show: VITE_API_BASE_URL=http://localhost:5000
```

---

## Completion Checklist

- [ ] All test scenarios passed
- [ ] No critical errors in console
- [ ] Backend API responding correctly
- [ ] Calendar events display properly
- [ ] AI chatbot responds to messages
- [ ] Error handling works gracefully
- [ ] Loading states are clear
- [ ] UI is responsive and smooth

---

## Next Steps After Testing

If all tests pass:
1. ✅ Integration is complete and working
2. Consider adding more features (see INTEGRATION_GUIDE.md)
3. Deploy to production environment
4. Add monitoring and analytics

If tests fail:
1. Check INTEGRATION_GUIDE.md troubleshooting section
2. Verify backend is running and configured
3. Check browser console for specific errors
4. Review backend logs for API errors
5. Ensure Google Calendar OAuth is set up correctly
