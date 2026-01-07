# 🎯 Enhanced Job Discovery - Google & Company Websites

## ✨ New Features Added

### 1. Google Jobs Search
- **Best for**: Aggregating jobs from multiple sources
- **Why it's great**: Google searches across LinkedIn, Indeed, company websites, and more
- **Usage**: Just check "Google Jobs" in the web interface
- **No login required**: Works immediately!

### 2. Company Website Search
- **Search specific companies directly**: Microsoft, Google, Amazon, etc.
- **How to use**: 
  - In web interface: Enter company names in "Search Specific Company Websites"
  - Example: `Microsoft, Google, Amazon`
  - Or in code: `sources = ["company:Microsoft", "company:Google"]`

### 3. Additional Job Boards Added
- **Monster** - Major job board
- **SimplyHired** - Job aggregator
- **CareerBuilder** - Major job board  
- **AngelList/Wellfound** - Startup jobs
- **RemoteOK** - Remote-only jobs

---

## 📊 Total Job Boards Available

You now have **12+ job boards** to search:

1. ✅ **Google Jobs** (NEW - Recommended!)
2. ✅ **Indeed**
3. **LinkedIn** (requires login)
4. **ZipRecruiter**
5. **Glassdoor**
6. **Dice**
7. ✅ **Monster** (NEW)
8. ✅ **SimplyHired** (NEW)
9. ✅ **CareerBuilder** (NEW)
10. ✅ **AngelList/Wellfound** (NEW)
11. ✅ **RemoteOK** (NEW - Remote only)
12. **Built In**

---

## 🚀 Recommended Configuration

### For Maximum Job Discovery

In the web interface:
- ✅ Check: **Google Jobs** (aggregates from many sources)
- ✅ Check: **Indeed**
- ✅ Check: **ZipRecruiter**
- ✅ Check: **SimplyHired**
- ✅ Check: **Monster**

Then add specific companies:
- Enter: `Microsoft, Google, Amazon, Apple, Meta`

This will search:
- Google Jobs (finds jobs from all major boards)
- 4 major job boards directly
- 5 company websites directly

**Result**: Maximum job coverage! 🎯

### For Tech Jobs Specifically

- ✅ Google Jobs
- ✅ Dice
- ✅ Built In
- ✅ AngelList
- ✅ RemoteOK
- Companies: `Google, Microsoft, Amazon, Meta, Apple, Netflix`

### For Remote Jobs

- ✅ RemoteOK (remote only)
- ✅ Google Jobs (filter by "Remote")
- ✅ Indeed (filter by location: "Remote")
- ✅ SimplyHired (filter by "Remote")

---

## 💡 Pro Tips

### 1. Google Jobs is Your Friend
Google Jobs aggregates from:
- LinkedIn
- Indeed
- Company websites
- Job boards
- And more!

**Recommendation**: Always include Google Jobs in your search.

### 2. Company-Specific Searches
Searching company websites directly helps you:
- Find jobs not posted on job boards
- Discover early postings
- Access internal referrals easier

**Top companies to search**:
- Tech: `Google, Microsoft, Amazon, Apple, Meta, Netflix, Adobe, Salesforce`
- Finance: `JPMorgan, Goldman Sachs, Bank of America, Citigroup`
- Consulting: `McKinsey, BCG, Deloitte, Accenture`

### 3. Combine Strategies
Best approach:
1. **Broad search**: Google Jobs + Indeed + ZipRecruiter (finds everything)
2. **Targeted search**: Specific companies you're interested in
3. **Niche boards**: Dice (tech), RemoteOK (remote), AngelList (startups)

---

## 🔧 How to Use Company Website Search

### In Web Interface:
1. Fill in "Search Specific Company Websites" field
2. Enter company names separated by commas
3. Example: `Microsoft, Google, Amazon, Apple`
4. Click "Start Job Discovery"

### In Code:
```python
sources = [
    "google",
    "indeed", 
    "company:Microsoft",
    "company:Google",
    "company:Amazon"
]
```

---

## 📈 Expected Results

With all sources enabled:
- **Google Jobs**: 50+ jobs (aggregated)
- **Indeed**: 25 jobs
- **ZipRecruiter**: 25 jobs
- **SimplyHired**: 25 jobs
- **Monster**: 25 jobs
- **Company websites**: 5-20 jobs each

**Total**: 150-200+ unique jobs per search! 🚀

After filtering:
- Remove duplicates (Google Jobs may overlap with others)
- Filter by keywords
- Filter by fit score

**Final**: 50-100 high-quality jobs to apply to

---

## ⚡ Quick Start

1. **Open web interface**: `http://localhost:8000/dashboard`
2. **Select job boards**:
   - ✅ Google Jobs
   - ✅ Indeed
   - ✅ ZipRecruiter
   - ✅ SimplyHired
3. **Add companies**: `Microsoft, Google, Amazon`
4. **Set jobs per source**: 25
5. **Click "Start Job Discovery"**

Watch as it discovers 100+ jobs automatically! 🎉

---

## 🎯 Success Tips

1. **Start with Google Jobs**: It's the easiest and most comprehensive
2. **Add 2-3 major boards**: Indeed, ZipRecruiter are reliable
3. **Target 3-5 companies**: Focus on companies you really want
4. **Adjust filters**: Use exclude keywords to remove senior roles
5. **Monitor results**: Check which sources give best matches

Enjoy your expanded job discovery! 🚀






