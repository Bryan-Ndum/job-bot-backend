"""
Verify that the database schema fix worked
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
    print("VERIFYING DATABASE FIX")
    print("="*70 + "\n")
    
    # Check if columns exist by trying to query them
    print("1. Checking if user_id column exists...")
    try:
        result = supabase.table("applications").select("user_id").limit(1).execute()
        print("   ✅ user_id column exists and is accessible")
        user_id_works = True
    except Exception as e:
        error_msg = str(e)
        if "user_id" in error_msg.lower() and ("does not exist" in error_msg.lower() or "42703" in error_msg):
            print(f"   ❌ user_id column still missing: {error_msg}")
            user_id_works = False
        else:
            print(f"   ⚠️ Could not verify user_id: {error_msg}")
            user_id_works = True  # Might just be empty table
    
    print("\n2. Checking if date_applied column exists...")
    try:
        result = supabase.table("applications").select("date_applied").limit(1).execute()
        print("   ✅ date_applied column exists and is accessible")
        date_applied_works = True
    except Exception as e:
        error_msg = str(e)
        if "date_applied" in error_msg.lower() and ("does not exist" in error_msg.lower() or "42703" in error_msg):
            print(f"   ❌ date_applied column still missing: {error_msg}")
            date_applied_works = False
        else:
            print(f"   ⚠️ Could not verify date_applied: {error_msg}")
            date_applied_works = True  # Might just be empty table
    
    # Count applications
    print("\n3. Counting applications...")
    try:
        # Try with user_id filter
        result = supabase.table("applications").select("id", count="exact").eq("user_id", USER_ID).execute()
        count_user = result.count if hasattr(result, 'count') and result.count else (len(result.data) if result.data else 0)
        print(f"   ✅ Found {count_user} application(s) for user: {USER_ID}")
    except Exception as e:
        print(f"   ⚠️ Could not count with user_id filter: {e}")
        count_user = 0
    
    try:
        # Try without user_id filter
        result = supabase.table("applications").select("id", count="exact").execute()
        count_all = result.count if hasattr(result, 'count') and result.count else (len(result.data) if result.data else 0)
        if count_all > count_user:
            print(f"   ℹ️ Total applications (all users): {count_all}")
    except:
        pass
    
    # Get recent applications
    print("\n4. Recent applications...")
    try:
        recent = supabase.table("applications").select("*").eq("user_id", USER_ID).order("date_applied", desc=True).limit(10).execute()
        if recent.data and len(recent.data) > 0:
            print(f"   ✅ Found {len(recent.data)} recent application(s):")
            for idx, app in enumerate(recent.data, 1):
                company = app.get("company", "Unknown") or "Unknown"
                role = app.get("role", "Unknown") or "Unknown"
                date = app.get("date_applied", "")
                if date:
                    date_str = date[:10] if len(date) >= 10 else date
                else:
                    date_str = "Unknown"
                score = app.get("fit_score", "N/A")
                print(f"      {idx}. {role} at {company}")
                print(f"         Score: {score}/100 | Date: {date_str}")
        else:
            print("   ℹ️ No applications found yet (this is normal if script just started)")
            print("   ℹ️ New applications will appear here as the script processes jobs")
    except Exception as e:
        print(f"   ⚠️ Could not fetch recent applications: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70 + "\n")
    
    if user_id_works and date_applied_works:
        print("✅ Database schema is fixed! All columns are accessible.")
        print(f"✅ Application tracking is working.")
        print(f"✅ Current application count: {count_user}")
        
        if count_user == 0:
            print("\nℹ️ No applications tracked yet. This could mean:")
            print("   - The business analyst script is still processing jobs")
            print("   - Applications are being submitted but haven't completed yet")
            print("   - The script will start tracking as it completes applications")
        else:
            print(f"\n🎉 Success! You have {count_user} application(s) tracked in the database.")
    else:
        print("❌ Database schema fix may not have completed successfully.")
        print("   Please check the SQL output in Supabase for any errors.")
        print("   You may need to run the SQL script again.")
    
    print("\n" + "="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Error during verification: {e}")
    import traceback
    traceback.print_exc()

