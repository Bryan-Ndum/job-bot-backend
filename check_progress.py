"""
Check progress of job applications
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from app.core.supabase_client import get_supabase
    
    supabase = get_supabase()
    USER_ID = "bryan_test"
    
    print("\n" + "="*70)
    print("📊 APPLICATION PROGRESS")
    print("="*70 + "\n")
    
    # Count total applications
    try:
        result = supabase.table("applications").select("id", count="exact").eq("user_id", USER_ID).execute()
        total_count = result.count if hasattr(result, 'count') and result.count else (len(result.data) if result.data else 0)
        print(f"✅ Total Applications: {total_count}\n")
    except Exception as e:
        print(f"⚠️ Could not count applications: {e}\n")
        total_count = 0
    
    # Get recent applications (last 20)
    print("📋 Recent Applications:\n")
    try:
        recent = supabase.table("applications").select("*").eq("user_id", USER_ID).order("date_applied", desc=True).limit(20).execute()
        if recent.data and len(recent.data) > 0:
            for idx, app in enumerate(recent.data, 1):
                company = app.get("company", "Unknown") or "Unknown"
                role = app.get("role", "Unknown") or "Unknown"
                date = app.get("date_applied", "")
                score = app.get("fit_score", "N/A")
                status = app.get("callback_status", "pending")
                
                if date:
                    # Format date nicely
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                        date_str = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        date_str = date[:16] if len(date) >= 16 else date
                else:
                    date_str = "Unknown"
                
                # Show emoji based on status
                status_emoji = {
                    "pending": "⏳",
                    "callback": "📞",
                    "interview": "🎯",
                    "rejected": "❌",
                    "no_response": "📭"
                }.get(status, "📄")
                
                print(f"   {idx}. {status_emoji} {role} at {company}")
                print(f"      Score: {score}/100 | Status: {status} | Date: {date_str}")
                print()
        else:
            print("   ℹ️ No applications found yet.")
            print("   The script may still be searching for jobs or processing applications.\n")
    except Exception as e:
        print(f"   ⚠️ Could not fetch recent applications: {e}\n")
    
    # Check if Python processes are running
    print("="*70)
    print("🖥️ PROCESS STATUS")
    print("="*70 + "\n")
    
    import subprocess
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        python_count = result.stdout.count('python.exe')
        if python_count > 0:
            print(f"✅ {python_count} Python process(es) running")
            print("   The application script is likely still active.\n")
        else:
            print("ℹ️ No Python processes found")
            print("   The script may have completed or stopped.\n")
    except:
        print("⚠️ Could not check running processes\n")
    
    # Progress summary
    print("="*70)
    print("📈 PROGRESS SUMMARY")
    print("="*70 + "\n")
    
    if total_count > 0:
        print(f"✅ {total_count} application(s) successfully submitted and tracked!")
        if total_count >= 10:
            print("🎯 Target of 10 applications reached!")
        else:
            remaining = 10 - total_count
            print(f"🎯 {remaining} more application(s) needed to reach target of 10")
    else:
        print("⏳ No applications tracked yet.")
        print("   The script may still be:")
        print("   - Searching for jobs")
        print("   - Processing applications")
        print("   - Waiting for applications to complete")
    
    print("\n" + "="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Error checking progress: {e}")
    import traceback
    traceback.print_exc()

