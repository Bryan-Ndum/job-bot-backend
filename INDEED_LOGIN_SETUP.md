# 🔐 Indeed Login Setup Guide

## Why Indeed Login is Needed

Indeed **does not require login for searching jobs**, but **applications require login** for:
- Resume upload
- Application tracking
- Email confirmations
- Saving application status

## Current Solution: Manual Login

When you apply to an Indeed job:

1. **The bot will detect** if Indeed requires login
2. **Browser window opens** showing the Indeed login page
3. **You manually log in** using your Indeed credentials
4. **The bot waits** for you to complete login (up to 60 seconds)
5. **Application continues** automatically after login

### Your Indeed Credentials
- **Email**: The email you used to create your Indeed account
- **Password**: Your Indeed account password

If you don't have an Indeed account, create one at: https://www.indeed.com/

## How It Works

When you run job applications:
```
🔐 Checking if Indeed login is required...
⚠️ Indeed login required. Please log in manually in the browser window.
   After logging in, the application will continue...
   ⏳ Waiting for login (max 60 seconds)...
   ✅ Login detected! Continuing with application...
```

## Future: Automated Login (Coming Soon)

We're working on automated login support where you can set:
- `INDEED_EMAIL` environment variable
- `INDEED_PASSWORD` environment variable

Then the bot will log in automatically. This feature is not yet available.

## ✅ Good News: Login Persists Indefinitely!

**With the current setup, you only need to log in once!**

The system uses a **persistent browser context** that saves your login session (cookies) indefinitely. Here's how it works:

1. **First Time**: Log into any job board (Indeed, LinkedIn, etc.) when the browser opens
   - You have **4 minutes** to complete the login
2. **Cookies Saved**: Your login session is saved to disk in `storage/browser_context/`
3. **Next Time**: The browser automatically loads your saved session - you're already logged in! 🎉
4. **Indefinitely**: Your login persists indefinitely (until you delete the browser context folder)

**Login Time**: You have **4 minutes** to log in when prompted. The bot will wait and detect when you're logged in automatically.

**Note**: Your login persists until you manually delete the `storage/browser_context/` folder.

So yes - **log in once, and you're good to go for all future applications!** 🚀

