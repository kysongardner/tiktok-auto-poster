# Troubleshooting Guide

## Issue: Script Gets Stuck After "Waiting for dashboard to load"

### Changes Made:

1. **Added URL verification**: The script now checks if the URL actually changes from the login page
2. **Added timeout protection**: If still on login page after 20 seconds, it will alert you
3. **Added progress indicators**: Dots (...) show while waiting for dashboard
4. **Added screenshots**: 
   - `dashboard_loaded.png` - saved when dashboard loads
   - `login_timeout.png` - saved if login fails
   - `before_post.png` - saved before starting to post

5. **Enhanced debugging output**:
   - Shows current URL after login
   - Lists dashboard elements found
   - Better error messages

### Common Causes:

1. **Two-Factor Authentication (2FA)**: Buffer may require 2FA verification
   - **Solution**: Manually approve the login, or disable 2FA temporarily

2. **Incorrect Credentials**: Email/password might be wrong
   - **Solution**: Check your `.env` file

3. **Slow Internet**: Page takes longer than expected to load
   - **Solution**: Script now waits up to 20 seconds and shows progress

4. **Cloudflare/Bot Detection**: Buffer might be blocking automated logins
   - **Solution**: May need to use a different approach or login manually first

### How to Debug:

1. **Check the screenshots** created in your folder:
   - `dashboard_loaded.png` - Did it actually load the dashboard?
   - `login_timeout.png` - Are you stuck on login page?

2. **Watch the console output** for:
   - Current URL after login
   - Dashboard elements detected
   - Any error messages

3. **Manual test**:
   ```powershell
   python auto_poster_windows.py
   ```
   Watch the browser window carefully - does it actually log in?

### Next Steps if Still Stuck:

1. **Verify login manually**: Try logging into Buffer in a regular browser with the same credentials
2. **Check for 2FA prompts**: The script can't handle 2FA automatically
3. **Check console output**: Look for the "Current URL after login" message
4. **Share the URL**: If the URL shows you're on a different page (like 2FA verification), we'll need to handle that

### Quick Fix Options:

**Option 1 - Manual Login Session:**
If Buffer requires 2FA, you could:
1. Manually log in once in Chrome
2. Save the session/cookies
3. Reuse them in the script

**Option 2 - Extended Wait:**
If it's just slow loading, increase the wait time in the script (currently 20 seconds).

**Option 3 - Different Approach:**
Instead of Buffer, consider posting directly to TikTok API (if available).
