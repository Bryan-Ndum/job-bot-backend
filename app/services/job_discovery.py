"""
Job Discovery and Search Module
Searches job boards and collects job URLs for automated application.
"""

import os
import time
from typing import List, Dict, Optional
# Apply nest_asyncio before importing Playwright to allow sync API in async contexts
try:
    import nest_asyncio
    nest_asyncio.apply()
except (ImportError, Exception):
    pass
from playwright.sync_api import sync_playwright, Page
import re


class JobDiscovery:
    """Discovers jobs from various job boards."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
    
    def start(self):
        """Initialize browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = self.browser.new_page()
        
        # Add stealth features
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
    
    def stop(self):
        """Close browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def search_linkedin_jobs(
        self,
        keywords: str,
        location: str = "",
        experience_level: str = "1",  # 1=Entry, 2=Associate, 3=Mid-Senior
        limit: int = 25
    ) -> List[Dict]:
        """
        Search LinkedIn jobs and return job URLs.
        
        Args:
            keywords: Job search keywords (e.g., "cybersecurity analyst")
            location: Location filter (e.g., "Morrisville, North Carolina")
            experience_level: Experience level filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries with url, title, company, location
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build LinkedIn jobs search URL
            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                "keywords": keywords,
                "location": location,
                "f_E": experience_level,
                "f_TPR": "r86400",  # Past 24 hours
                "position": "1",
                "pageNum": "0"
            }
            
            query_string = "&".join([f"{k}={v}" for k, v in params.items() if v])
            search_url = f"{base_url}?{query_string}"
            
            print(f"🔍 Searching LinkedIn jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)  # Wait for results to load
            
            # Scroll to load more results
            for _ in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator(".jobs-search-results__list-item").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a.job-card-list__title").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.linkedin.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator(".job-card-container__primary-description").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator(".job-card-container__metadata-item").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else ""
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "linkedin",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ LinkedIn search error: {e}")
        
        return jobs
    
    def search_indeed_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search Indeed jobs and return job URLs.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build Indeed search URL
            base_url = "https://www.indeed.com/jobs"
            query = keywords.replace(" ", "+")
            loc_query = location.replace(" ", "+").replace(",", "%2C")
            
            if location:
                search_url = f"{base_url}?q={query}&l={loc_query}&fromage=1"
            else:
                search_url = f"{base_url}?q={query}&fromage=1"
            
            print(f"🔍 Searching Indeed jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator(".job_seen_beacon, .job_seen_beacon_v3").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a.jcs-JobTitle, h2.jobTitle a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.indeed.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator(".companyName, [data-testid='company-name']").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator(".companyLocation, [data-testid='job-location']").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else ""
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "indeed",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ Indeed search error: {e}")
        
        return jobs
    
    def search_ziprecruiter_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search ZipRecruiter jobs and return job URLs.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build ZipRecruiter search URL
            base_url = "https://www.ziprecruiter.com/jobs-search"
            query = keywords.replace(" ", "-")
            loc_query = location.replace(" ", "-").replace(",", "-").lower() if location else "remote"
            
            search_url = f"{base_url}?search={query}&location={loc_query}"
            
            print(f"🔍 Searching ZipRecruiter jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings - ZipRecruiter uses various selectors
            job_cards = self.page.locator(".job_content, article[data-job-id], .job_result").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a[href*='/job/'], .job_link, h2 a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.ziprecruiter.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator(".company_name, .t_company_link, [data-testid='company-name']").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator(".location, .job_location, [data-testid='job-location']").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else ""
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "ziprecruiter",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ ZipRecruiter search error: {e}")
        
        return jobs
    
    def search_glassdoor_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search Glassdoor jobs and return job URLs.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build Glassdoor search URL
            base_url = "https://www.glassdoor.com/Job/jobs.htm"
            query = keywords.replace(" ", "+")
            loc_query = location.replace(" ", "+").replace(",", "%2C") if location else ""
            
            if location:
                search_url = f"{base_url}?sc.keyword={query}&locT=C&locId={loc_query}"
            else:
                search_url = f"{base_url}?sc.keyword={query}"
            
            print(f"🔍 Searching Glassdoor jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)  # Glassdoor can be slow to load
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator("[data-test='job-listing'], .react-job-listing, .JobCard").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a[data-test='job-link'], a.jobLink, .jobLink a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.glassdoor.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator("[data-test='employer-name'], .employerName, .jobInfoItem").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator("[data-test='job-location'], .loc, .jobLocation").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else ""
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "glassdoor",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ Glassdoor search error: {e}")
        
        return jobs
    
    def search_dice_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search Dice (tech jobs) and return job URLs.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build Dice search URL
            base_url = "https://www.dice.com/jobs"
            query = keywords.replace(" ", "%20")
            loc_query = location.replace(" ", "%20").replace(",", "%2C") if location else ""
            
            if location:
                search_url = f"{base_url}?q={query}&l={loc_query}"
            else:
                search_url = f"{base_url}?q={query}"
            
            print(f"🔍 Searching Dice jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator("[data-testid='job-card'], .search-result, .card").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a[data-cy='card-title-link'], a.card-title-link, h5 a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.dice.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator("[data-cy='search-result-company-name'], .card-company, .companyName").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator("[data-cy='search-result-location'], .card-location, .jobLocation").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else ""
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "dice",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ Dice search error: {e}")
        
        return jobs
    
    def search_builtin_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search Built In (tech startup jobs) and return job URLs.
        Supports multiple cities: NYC, SF, Austin, Chicago, Boston, etc.
        
        Args:
            keywords: Job search keywords
            location: Location filter (city name like "New York", "San Francisco", "Remote")
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Map common locations to Built In city codes
            location_map = {
                "new york": "nyc",
                "san francisco": "sf",
                "austin": "austin",
                "chicago": "chicago",
                "boston": "boston",
                "seattle": "seattle",
                "los angeles": "la",
                "remote": "remote"
            }
            
            # Determine city from location
            city = "remote"  # Default
            location_lower = location.lower() if location else ""
            for key, value in location_map.items():
                if key in location_lower:
                    city = value
                    break
            
            # Build Built In search URL
            base_url = f"https://www.builtin.com/jobs/{city}"
            query = keywords.replace(" ", "-").lower()
            
            search_url = f"{base_url}?search={query}"
            
            print(f"🔍 Searching Built In ({city}) jobs: {keywords}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator(".job-row, .job-card, [data-id='job-card']").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a[href*='/jobs/'], .job-title a, h3 a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.builtin.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator(".company-name, .company, [data-test='company-name']").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator(".job-location, .location, [data-test='job-location']").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else location
            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "builtin",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ Built In search error: {e}")
        
        return jobs
    
    def search_google_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search Google Jobs (aggregates from multiple job boards).
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build Google Jobs search URL
            base_url = "https://www.google.com/search"
            query = f"{keywords} jobs"
            if location:
                query += f" in {location}"
            
            search_url = f"{base_url}?q={query.replace(' ', '+')}&ibp=htl;jobs"
            
            print(f"🔍 Searching Google Jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings - Google Jobs uses various selectors
            job_cards = self.page.locator("[data-ved], .PwjeAc, [jsname='f0kZJb']").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL - Google Jobs links to original job posting
                    link = card.locator("a[href*='jobs'], a[href*='linkedin'], a[href*='indeed']").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.google.com{href}"
                            
                            # Get job title
                            title_elem = card.locator("h2, .BjJfJf, [role='heading']").first
                            title = title_elem.text_content().strip() if title_elem.is_visible(timeout=1000) else ""
                            
                            # Get company name
                            company_elem = card.locator(".nJlQNd, .sMzDkb, [data-company-name]").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator(".Qk80Jf, [data-location]").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else location
                            
                            if title and job_url:
                                jobs.append({
                                    "url": job_url,
                                    "title": title,
                                    "company": company,
                                    "location": job_location,
                                    "source": "google",
                                    "keywords": keywords
                                })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ Google Jobs search error: {e}")
        
        return jobs
    
    def search_monster_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search Monster jobs and return job URLs.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build Monster search URL
            base_url = "https://www.monster.com/jobs/search"
            query = keywords.replace(" ", "-")
            loc_query = location.replace(" ", "-") if location else ""
            
            if location:
                search_url = f"{base_url}?q={query}&where={loc_query}"
            else:
                search_url = f"{base_url}?q={query}"
            
            print(f"🔍 Searching Monster jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator("[data-testid='job-card'], .job-card, .card").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a[href*='/jobs/'], h2 a, .job-title a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.monster.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator(".company-name, [data-testid='company-name']").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator(".location, [data-testid='job-location']").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else ""
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "monster",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ Monster search error: {e}")
        
        return jobs
    
    def search_careerbuilder_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search CareerBuilder jobs and return job URLs.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build CareerBuilder search URL
            base_url = "https://www.careerbuilder.com/jobs"
            query = keywords.replace(" ", "+")
            loc_query = location.replace(" ", "+") if location else ""
            
            if location:
                search_url = f"{base_url}?keywords={query}&location={loc_query}"
            else:
                search_url = f"{base_url}?keywords={query}"
            
            print(f"🔍 Searching CareerBuilder jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator(".data-results-content-parent, .job-row, [data-job-id]").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a[href*='/job/'], .data-results-content a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.careerbuilder.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator(".data-details, .company-name").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator(".data-details span, .location").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else ""
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "careerbuilder",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ CareerBuilder search error: {e}")
        
        return jobs
    
    def search_simplyhired_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search SimplyHired jobs and return job URLs.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build SimplyHired search URL
            base_url = "https://www.simplyhired.com/search"
            query = keywords.replace(" ", "+")
            loc_query = location.replace(" ", "+").replace(",", "%2C") if location else ""
            
            if location:
                search_url = f"{base_url}?q={query}&l={loc_query}"
            else:
                search_url = f"{base_url}?q={query}"
            
            print(f"🔍 Searching SimplyHired jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator("[data-jobkey], .SerpJob, .job-card").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a[href*='/job/'], h2 a, .jobtitle a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://www.simplyhired.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator(".company, .jobposting-company").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator(".jobposting-location, .location").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else ""
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "simplyhired",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ SimplyHired search error: {e}")
        
        return jobs
    
    def search_angellist_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search AngelList (Wellfound) jobs - great for startups.
        
        Args:
            keywords: Job search keywords
            location: Location filter (or "Remote")
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build AngelList search URL
            base_url = "https://wellfound.com/role_locations"
            query = keywords.replace(" ", "-").lower()
            loc_query = "remote" if "remote" in location.lower() else location.replace(" ", "-").lower() if location else ""
            
            if location:
                search_url = f"{base_url}?search={query}&locations[]={loc_query}"
            else:
                search_url = f"{base_url}?search={query}"
            
            print(f"🔍 Searching AngelList jobs: {keywords} in {location or 'Anywhere'}")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator("[data-test='JobCard'], .job-card, .startup-job-listing").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a[href*='/role/'], h3 a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://wellfound.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator("[data-test='CompanyName'], .company-name").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            # Get location
                            location_elem = card.locator(".location, [data-test='JobLocation']").first
                            job_location = location_elem.text_content().strip() if location_elem.is_visible(timeout=1000) else location
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": job_location,
                                "source": "angellist",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ AngelList search error: {e}")
        
        return jobs
    
    def search_remoteok_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search RemoteOK jobs - remote jobs only.
        
        Args:
            keywords: Job search keywords
            location: Ignored (all jobs are remote)
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Build RemoteOK search URL
            base_url = "https://remoteok.com"
            query = keywords.replace(" ", "-")
            
            search_url = f"{base_url}/remote-{query}-jobs"
            
            print(f"🔍 Searching RemoteOK jobs: {keywords} (Remote only)")
            print(f"   URL: {search_url}")
            
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Scroll to load more
            for _ in range(2):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Find job listings
            job_cards = self.page.locator("tr.job, [data-job-id], .job-listing").all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a[href*='/remote-jobs/'], h2 a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"https://remoteok.com{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Get company name
                            company_elem = card.locator("[data-company], .company").first
                            company = company_elem.text_content().strip() if company_elem.is_visible(timeout=1000) else ""
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company,
                                "location": "Remote",
                                "source": "remoteok",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs")
            
        except Exception as e:
            print(f"   ⚠️ RemoteOK search error: {e}")
        
        return jobs
    
    def search_company_website(
        self,
        company_name: str,
        keywords: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search a specific company's careers/jobs page.
        
        Args:
            company_name: Name of the company (e.g., "Microsoft", "Google")
            keywords: Job search keywords (optional filter)
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if not self.page:
            self.start()
        
        try:
            # Common careers page URL patterns
            company_lower = company_name.lower().replace(" ", "")
            possible_urls = [
                f"https://www.{company_lower}.com/careers",
                f"https://www.{company_lower}.com/jobs",
                f"https://careers.{company_lower}.com",
                f"https://jobs.{company_lower}.com",
                f"https://{company_lower}.com/careers/jobs",
            ]
            
            careers_url = None
            for url in possible_urls:
                try:
                    self.page.goto(url, wait_until="domcontentloaded", timeout=10000)
                    if "job" in self.page.content().lower() or "career" in self.page.content().lower():
                        careers_url = url
                        break
                except:
                    continue
            
            if not careers_url:
                print(f"   ⚠️ Could not find careers page for {company_name}")
                return jobs
            
            print(f"🔍 Searching {company_name} careers page: {careers_url}")
            
            # Try to find job listings with common selectors
            job_cards = self.page.locator(
                "[data-job-id], .job-posting, .job-listing, .career-item, "
                "a[href*='job'], a[href*='career'], [class*='job'], [class*='position']"
            ).all()
            
            print(f"   Found {len(job_cards)} job listings")
            
            for card in job_cards[:limit]:
                try:
                    # Get job URL
                    link = card.locator("a").first
                    if link.is_visible(timeout=2000):
                        href = link.get_attribute("href")
                        if href:
                            job_url = href if href.startswith("http") else f"{careers_url.rstrip('/')}{href}"
                            
                            # Get job title
                            title = link.text_content().strip() if link.is_visible() else ""
                            
                            # Filter by keywords if provided
                            if keywords and keywords.lower() not in title.lower():
                                continue
                            
                            jobs.append({
                                "url": job_url,
                                "title": title,
                                "company": company_name,
                                "location": "",
                                "source": f"company-{company_name.lower()}",
                                "keywords": keywords
                            })
                except Exception as e:
                    continue
            
            print(f"   ✅ Collected {len(jobs)} job URLs from {company_name}")
            
        except Exception as e:
            print(f"   ⚠️ Company website search error for {company_name}: {e}")
        
        return jobs
    
    def search_greenhouse_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 25
    ) -> List[Dict]:
        """
        Search Greenhouse job board (jobs.greenhouse.io aggregator).
        Note: Greenhouse doesn't have a unified job board, so this searches
        common Greenhouse-powered company career pages.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Greenhouse doesn't have a unified search, but we can search
        # for jobs via job aggregators or specific company pages
        # For now, we'll note this limitation and return empty results
        # Users can manually add Greenhouse job URLs
        
        print(f"🔍 Greenhouse search: Greenhouse doesn't have a unified job board")
        print(f"   ⚠️ Please add Greenhouse job URLs manually or use company-specific searches")
        
        return jobs
    
    def search_jobs(
        self,
        keywords: str,
        location: str = "",
            sources: List[str] = ["linkedin", "indeed", "ziprecruiter", "glassdoor", "dice"],
        limit_per_source: int = 25
    ) -> List[Dict]:
        """
        Search multiple job boards and return combined results.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            sources: List of job boards to search (linkedin, indeed, ziprecruiter, glassdoor, dice, builtin, google, monster, careerbuilder, simplyhired, angellist, remoteok, company:CompanyName)
            limit_per_source: Maximum jobs per source
        
        Returns:
            Combined list of job dictionaries
        """
        all_jobs = []
        
        for source in sources:
            try:
                if source == "linkedin":
                    jobs = self.search_linkedin_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "indeed":
                    jobs = self.search_indeed_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "ziprecruiter":
                    jobs = self.search_ziprecruiter_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "glassdoor":
                    jobs = self.search_glassdoor_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "dice":
                    jobs = self.search_dice_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "builtin":
                    jobs = self.search_builtin_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "google":
                    jobs = self.search_google_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "monster":
                    jobs = self.search_monster_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "careerbuilder":
                    jobs = self.search_careerbuilder_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "simplyhired":
                    jobs = self.search_simplyhired_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "angellist":
                    jobs = self.search_angellist_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "remoteok":
                    jobs = self.search_remoteok_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source == "greenhouse":
                    jobs = self.search_greenhouse_jobs(keywords, location, limit=limit_per_source)
                    all_jobs.extend(jobs)
                elif source.startswith("company:"):
                    # Format: "company:Microsoft" or "company:Google"
                    company_name = source.replace("company:", "")
                    jobs = self.search_company_website(company_name, keywords, limit=limit_per_source)
                    all_jobs.extend(jobs)
                else:
                    print(f"   ⚠️ Unknown job board: {source}")
                    continue
                time.sleep(1)  # Rate limiting between sources (reduced for speed)
            except Exception as e:
                print(f"   ⚠️ Error searching {source}: {e}")
                continue
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                unique_jobs.append(job)
        
        print(f"\n📊 Total unique jobs found: {len(unique_jobs)}")
        
        return unique_jobs
    
    def filter_jobs(
        self,
        jobs: List[Dict],
        exclude_keywords: List[str] = None,
        include_keywords: List[str] = None,
        min_fit_score: int = 0
    ) -> List[Dict]:
        """
        Filter jobs based on keywords and criteria.
        
        Args:
            jobs: List of job dictionaries
            exclude_keywords: Keywords to exclude (e.g., ["senior", "manager"])
            include_keywords: Keywords that must be present
            min_fit_score: Minimum fit score (if available)
        
        Returns:
            Filtered list of jobs
        """
        filtered = []
        
        exclude_keywords = exclude_keywords or []
        include_keywords = include_keywords or []
        
        for job in jobs:
            # Combine title, company, location, and description for keyword matching
            description = job.get('description', '') or job.get('raw_description', '')
            text = f"{job.get('title', '')} {job.get('company', '')} {job.get('location', '')} {description}".lower()
            
            # Exclude jobs with exclude keywords
            if exclude_keywords:
                if any(keyword.lower() in text for keyword in exclude_keywords):
                    continue
            
            # Include only jobs with include keywords
            if include_keywords:
                if not any(keyword.lower() in text for keyword in include_keywords):
                    continue
            
            filtered.append(job)
        
        print(f"📋 Filtered jobs: {len(filtered)}/{len(jobs)} passed filters")
        
        return filtered


def discover_and_apply(
    keywords: str,
    location: str = "",
    user_info: Dict = None,
    user_id: str = "default",
            sources: List[str] = ["linkedin", "indeed", "ziprecruiter", "glassdoor", "dice"],
    limit_per_source: int = 25,
    exclude_keywords: List[str] = None,
    include_keywords: List[str] = None,
    min_fit_score: int = 65,
    auto_apply: bool = True,
    max_applications: int = None
) -> Dict:
    import time
    start_time = time.time()
    """
    Discover jobs online and apply to them automatically.
    
    Args:
        keywords: Job search keywords
        location: Location filter
        user_info: User information dict
        user_id: User identifier
        sources: Job boards to search
        limit_per_source: Max jobs per source
        exclude_keywords: Keywords to exclude
        include_keywords: Keywords to require
        min_fit_score: Minimum fit score to apply
        auto_apply: Whether to automatically apply
    
    Returns:
        Summary of discoveries and applications
    """
    from app.services.job_application_orchestrator import JobApplicationOrchestrator
    
    discovery = JobDiscovery(headless=False)
    orchestrator = JobApplicationOrchestrator(user_id, user_info)
    results = {
        "jobs_discovered": [],
        "jobs_filtered": [],
        "applications_submitted": [],
        "applications_skipped": [],
        "errors": []
    }
    
    try:
        discovery.start()
        
        # Step 1: Discover jobs
        print("\n" + "="*70)
        print("🔍 JOB DISCOVERY")
        print("="*70 + "\n")
        
        jobs = discovery.search_jobs(
            keywords=keywords,
            location=location,
            sources=sources,
            limit_per_source=limit_per_source
        )
        
        results["jobs_discovered"] = jobs
        
        # Step 2: Filter jobs
        print("\n📋 FILTERING JOBS\n")
        
        filtered_jobs = discovery.filter_jobs(
            jobs=jobs,
            exclude_keywords=exclude_keywords,
            include_keywords=include_keywords
        )
        
        results["jobs_filtered"] = filtered_jobs
        
        # Step 3: Apply to filtered jobs
        if auto_apply and filtered_jobs:
            print("\n" + "="*70)
            print("🚀 AUTO-APPLYING TO JOBS")
            print("="*70 + "\n")
            
            # Track applied URLs in this session to avoid duplicates
            applied_urls_in_session = set()
            
            for idx, job in enumerate(filtered_jobs, 1):
                job_url = job.get("url", "")
                
                # Skip if already applied in this session
                if job_url in applied_urls_in_session:
                    print(f"\n[{idx}/{len(filtered_jobs)}] ⏭️ Skipping duplicate: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                    continue
                
                print(f"\n[{idx}/{len(filtered_jobs)}] Processing: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"   URL: {job.get('url', 'N/A')}")
                
                try:
                    result = orchestrator.process_job_url(
                        url=job["url"],
                        auto_apply=True,
                        min_fit_score=min_fit_score
                    )
                    
                    if result.get("status") == "applied":
                        applied_urls_in_session.add(job_url)  # Track as applied
                        results["applications_submitted"].append({
                            "job": job,
                            "application_id": result.get("application_id"),
                            "fit_score": result.get("fit_score"),
                            "status": result.get("status")
                        })
                        applied_count = len(results["applications_submitted"])
                        print(f"   ✅ Application submitted (Fit: {result.get('fit_score', 0)}/100) - Total: {applied_count}")
                        
                        # Stop if we've reached max_applications
                        if max_applications and applied_count >= max_applications:
                            print(f"\n🎯 Reached target of {max_applications} successful applications. Stopping...")
                            break
                    elif result.get("status") == "duplicate":
                        applied_urls_in_session.add(job_url)  # Track as duplicate
                        results["applications_skipped"].append({
                            "job": job,
                            "reason": result.get("reason", "Duplicate application"),
                            "fit_score": result.get("fit_score", 0)
                        })
                        print(f"   ⏭️ Skipped: {result.get('reason', 'Duplicate')}")
                    else:
                        results["applications_skipped"].append({
                            "job": job,
                            "reason": result.get("reason", "Unknown"),
                            "fit_score": result.get("fit_score", 0)
                        })
                        print(f"   ⏭️ Skipped: {result.get('reason', 'Unknown')} (Fit: {result.get('fit_score', 0)}/100)")
                    
                    # Rate limiting - wait between applications (reduced for speed)
                    if idx < len(filtered_jobs):
                        print("   ⏳ Waiting 3 seconds before next application...")
                        time.sleep(3)
                        
                except Exception as e:
                    error_msg = str(e)
                    results["errors"].append({
                        "job": job,
                        "error": error_msg
                    })
                    print(f"   ❌ Error: {error_msg}")
                    continue
        
        # Calculate duration
        duration = time.time() - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        if minutes > 0:
            duration_str = f"{minutes}m {seconds}s"
        else:
            duration_str = f"{seconds}s"
        
        # Print summary
        print("\n" + "="*70)
        print("📊 DISCOVERY AND APPLICATION SUMMARY")
        print("="*70 + "\n")
        
        print(f"Jobs Discovered: {len(results['jobs_discovered'])}")
        print(f"Jobs After Filtering: {len(results['jobs_filtered'])}")
        print(f"Applications Submitted: {len(results['applications_submitted'])}")
        print(f"Applications Skipped: {len(results['applications_skipped'])}")
        print(f"Errors: {len(results['errors'])}")
        print(f"⏱️  Total Duration: {duration_str}")
        
        if results['applications_submitted']:
            print("\n✅ Successfully Applied To:")
            for app in results['applications_submitted']:
                job = app['job']
                print(f"   - {job.get('title', 'N/A')} at {job.get('company', 'N/A')} (Fit: {app.get('fit_score', 0)}/100)")
        
        if results['errors']:
            print("\n❌ Errors Encountered:")
            for err in results['errors']:
                job = err['job']
                print(f"   - {job.get('title', 'N/A')}: {err.get('error', 'Unknown error')}")
        
    finally:
        discovery.stop()
    
    # Add duration to results
    duration = time.time() - start_time
    results["duration_seconds"] = round(duration, 2)
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    if minutes > 0:
        results["duration"] = f"{minutes}m {seconds}s"
    else:
        results["duration"] = f"{seconds}s"
    
    return results

