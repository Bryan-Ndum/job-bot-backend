"""
Test the discovery endpoint locally to see the actual error
"""
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.job_discovery import discover_and_apply

print("Testing discover_and_apply function with minimal data...")
print("="*70)

try:
    # Minimal test data
    result = discover_and_apply(
        keywords="cybersecurity analyst",
        location="North Carolina",
        user_info={
            "first_name": "Bryan",
            "last_name": "Ndum",
            "email": "bryanndum12@gmail.com",
            "phone": "",
            "location": "Morrisville, North Carolina",
            "linkedin": ""
        },
        user_id="test_user",
        sources=["linkedin"],  # Just one source for testing
        limit_per_source=2,  # Just 2 jobs for testing
        exclude_keywords=None,
        include_keywords=None,
        min_fit_score=65,
        auto_apply=False  # Don't actually apply, just discover
    )
    
    print("\n✅ Success!")
    print(f"Jobs discovered: {len(result.get('jobs_discovered', []))}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()






