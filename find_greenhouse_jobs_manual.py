"""
Find Greenhouse Jobs - Provides manual list of known Greenhouse companies
Since Greenhouse jobs are harder to find through generic searches,
this provides a list of companies known to use Greenhouse for cybersecurity roles
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

print("\n" + "="*70)
print("🌱 FINDING GREENHOUSE JOBS FOR CYBERSECURITY")
print("="*70 + "\n")

print("Greenhouse jobs are often found on company career pages rather than job boards.")
print("Here are some well-known companies that use Greenhouse ATS:\n")

# Known companies that use Greenhouse (you can add more)
greenhouse_companies = [
    {
        "company": "IXL Learning",
        "career_page": "https://www.ixl.com/company/careers",
        "example_job": "https://www.ixl.com/company/careers/apply?gh_jid=8299922002",
        "notes": "You've applied here before - confirmed Greenhouse"
    },
    {
        "company": "Reddit",
        "career_page": "https://www.redditinc.com/careers",
        "notes": "Uses Greenhouse - search for security roles"
    },
    {
        "company": "GitHub",
        "career_page": "https://github.com/careers",
        "notes": "Uses Greenhouse - search for security roles"
    },
    {
        "company": "Slack",
        "career_page": "https://slack.com/careers",
        "notes": "Uses Greenhouse - search for security roles"
    },
    {
        "company": "Etsy",
        "career_page": "https://www.etsy.com/careers",
        "notes": "Uses Greenhouse - search for security roles"
    }
]

print("📋 KNOWN GREENHOUSE COMPANIES:\n")
for idx, company in enumerate(greenhouse_companies[:5], 1):
    print(f"{idx}. {company['company']}")
    print(f"   Career Page: {company.get('career_page', 'N/A')}")
    if 'example_job' in company:
        print(f"   Example Job: {company['example_job']}")
    if 'notes' in company:
        print(f"   Note: {company['notes']}")
    print()

print("="*70)
print("\n💡 RECOMMENDATION:")
print("   1. Visit these company career pages directly")
print("   2. Search for 'security' or 'cybersecurity' roles")
print("   3. Look for URLs containing 'greenhouse.io' or 'gh_jid' parameter")
print("   4. Use the application system with those Greenhouse URLs")
print("\n" + "="*70 + "\n")

