"""
Simple test to debug the discovery endpoint
"""
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.job_discovery import JobDiscovery

print("Testing JobDiscovery initialization...")

try:
    discovery = JobDiscovery(headless=False)
    print("✅ JobDiscovery created")
    
    print("Testing browser start...")
    discovery.start()
    print("✅ Browser started successfully!")
    
    discovery.stop()
    print("✅ Browser stopped successfully!")
    print("\n✅ All tests passed! JobDiscovery should work.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()






