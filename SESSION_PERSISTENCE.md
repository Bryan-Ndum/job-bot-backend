# 🔐 Session Persistence - How Login Works

## Good News: You Only Need to Log In Once!

The system uses **persistent browser contexts** to save your login sessions. Here's how it works:

## How It Works

1. **First Application Run**:
   - Browser opens (new session)
   - You log into Indeed/LinkedIn/etc. when prompted
   - Login cookies are **automatically saved** to `storage/browser_context/`

2. **Next Application Runs**:
   - Browser opens and **automatically loads saved cookies**
   - You're already logged in! ✅
   - No need to log in again

## What Gets Saved

- ✅ Login cookies
- ✅ Session tokens
- ✅ Authentication state

**Saved Location**: `storage/browser_context/`

## Login Time Window

**You have 4 minutes to complete login** when the browser opens. The bot will:
- Detect when you're logged in automatically
- Continue with the application once login is complete
- Show progress updates every 30 seconds

## When You Need to Log In Again

You'll need to log in again if:
- 🗑️ You delete the `storage/browser_context/` folder
- 🔒 You log out manually
- 🆕 You use a different computer

**Note**: Sessions persist indefinitely until manually deleted!

## Summary

**Answer**: **Yes, log in once, and it persists for all future applications!** 🎉

The system handles this automatically - you don't need to do anything special.

