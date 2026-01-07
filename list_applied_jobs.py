"""
List all jobs that have been applied to
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
    from datetime import datetime
    
    supabase = get_supabase()
    USER_ID = "bryan_test"
    
    print("\n" + "="*70)
    print("📋 JOBS APPLIED TO")
    print("="*70 + "\n")
    
    # Get all applications
    try:
        result = supabase.table("applications").select("*").eq("user_id", USER_ID).order("date_applied", desc=True).execute()
        
        if result.data and len(result.data) > 0:
            applications = result.data
            print(f"✅ Total Applications: {len(applications)}\n")
            print("-" * 70)
            
            for idx, app in enumerate(applications, 1):
                company = app.get("company", "Unknown") or "Unknown"
                role = app.get("role", "Unknown") or "Unknown"
                url = app.get("url", "") or ""
                date = app.get("date_applied", "")
                score = app.get("fit_score", "N/A")
                status = app.get("callback_status", "pending")
                app_id = app.get("application_id", "N/A")
                
                # Format date
                if date:
                    try:
                        # Handle ISO format with or without timezone
                        date_str = date.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(date_str)
                        date_formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                        time_ago = ""
                        
                        # Calculate time ago
                        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
                        delta = now - dt.replace(tzinfo=None) if dt.tzinfo else now - dt
                        
                        if delta.days > 0:
                            time_ago = f" ({delta.days} day{'s' if delta.days != 1 else ''} ago)"
                        elif delta.seconds >= 3600:
                            hours = delta.seconds // 3600
                            time_ago = f" ({hours} hour{'s' if hours != 1 else ''} ago)"
                        elif delta.seconds >= 60:
                            minutes = delta.seconds // 60
                            time_ago = f" ({minutes} minute{'s' if minutes != 1 else ''} ago)"
                        else:
                            time_ago = " (just now)"
                        
                        date_formatted += time_ago
                    except:
                        date_formatted = date[:19] if len(date) >= 19 else date
                else:
                    date_formatted = "Unknown date"
                
                # Status emoji
                status_emoji = {
                    "pending": "⏳",
                    "callback": "📞",
                    "interview": "🎯",
                    "rejected": "❌",
                    "no_response": "📭"
                }.get(status, "📄")
                
                print(f"\n{idx}. {status_emoji} {role}")
                print(f"   Company: {company}")
                print(f"   Fit Score: {score}/100")
                print(f"   Status: {status}")
                print(f"   Applied: {date_formatted}")
                print(f"   Application ID: {app_id}")
                
                if url:
                    # Truncate long URLs
                    display_url = url[:80] + "..." if len(url) > 80 else url
                    print(f"   URL: {display_url}")
                
                print("-" * 70)
            
            # Summary by status
            print("\n📊 SUMMARY BY STATUS:")
            status_counts = {}
            for app in applications:
                status = app.get("callback_status", "pending")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in sorted(status_counts.items()):
                emoji = {
                    "pending": "⏳",
                    "callback": "📞",
                    "interview": "🎯",
                    "rejected": "❌",
                    "no_response": "📭"
                }.get(status, "📄")
                print(f"   {emoji} {status.capitalize()}: {count}")
            
            # Average fit score
            scores = [app.get("fit_score") for app in applications if app.get("fit_score") is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
                print(f"\n📈 Average Fit Score: {avg_score:.1f}/100")
                print(f"📈 Highest Fit Score: {max(scores)}/100")
                print(f"📈 Lowest Fit Score: {min(scores)}/100")
            
        else:
            print("ℹ️ No applications found in database yet.\n")
            print("This could mean:")
            print("   - The script is still searching for jobs")
            print("   - Applications are being processed but not yet completed")
            print("   - The script hasn't found qualifying jobs yet")
            print("\n💡 Check back in a few minutes, or look for browser windows")
            print("   showing the application process.\n")
        
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Error fetching applications: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
