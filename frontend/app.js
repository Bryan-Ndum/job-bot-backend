// API Configuration
// Use config.js or environment variable
const API_BASE_URL = (() => {
  // Check if we're in production (deployed on Vercel)
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    // In production, use environment variable or fallback to your backend URL
    // You'll set this in Vercel dashboard as an environment variable
    return window.API_BASE_URL || 'https://your-backend-url.railway.app';
  }
  // Local development
  return 'http://localhost:8000';
})();

// State
let isRunning = false;
let currentResults = null;

// DOM Elements
const form = document.getElementById('discoveryForm');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const progressPanel = document.getElementById('progressPanel');
const resultsPanel = document.getElementById('resultsPanel');
const logOutput = document.getElementById('logOutput');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkApiHealth();
    loadApplicationHistory();
});

function setupEventListeners() {
    form.addEventListener('submit', handleStartDiscovery);
    stopBtn.addEventListener('click', handleStop);
    
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            switchTab(tab);
        });
    });
}

async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/jobs/health`);
        const data = await response.json();
        if (data.status === 'healthy') {
            log('✅ API is healthy and ready', 'success');
        }
    } catch (error) {
        log('⚠️ Could not connect to API. Make sure FastAPI server is running on ' + API_BASE_URL, 'warning');
    }
}

async function handleStartDiscovery(e) {
    e.preventDefault();
    
    if (isRunning) {
        return;
    }
    
    isRunning = true;
    startBtn.disabled = true;
    stopBtn.style.display = 'inline-block';
    progressPanel.style.display = 'block';
    resultsPanel.style.display = 'none';
    logOutput.innerHTML = '';
    
    // Get form data - convert to snake_case for backend
    let sources = Array.from(document.querySelectorAll('input[name="sources"]:checked')).map(cb => cb.value);
    
    // Add company website searches if provided
    const companyInput = document.getElementById('companySearches');
    if (companyInput && companyInput.value.trim()) {
        const companies = companyInput.value.split(',').map(c => c.trim()).filter(c => c);
        companies.forEach(company => {
            sources.push(`company:${company}`);
        });
    }
    
    const formData = {
        keywords: document.getElementById('keywords').value,
        location: document.getElementById('location').value,
        sources: sources,
        limit_per_source: parseInt(document.getElementById('jobsPerSource').value),
        exclude_keywords: document.getElementById('excludeKeywords').value.split(',').map(s => s.trim()).filter(s => s),
        min_fit_score: parseInt(document.getElementById('minFitScore').value),
        user_info: {
            first_name: document.getElementById('firstName').value,
            last_name: document.getElementById('lastName').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            location: document.getElementById('userLocation').value,
            linkedin: document.getElementById('linkedin').value
        },
        user_id: document.getElementById('email').value.split('@')[0], // Use email prefix as user_id
        auto_apply: true
    };
    
    log(`🚀 Starting job discovery: ${formData.keywords} in ${formData.location || 'Anywhere'}`, 'info');
    log(`📊 Sources: ${formData.sources.join(', ')}`, 'info');
    log(`⚙️ Minimum fit score: ${formData.min_fit_score}/100`, 'info');
    log('');
    
    try {
        // Call the discovery endpoint
        // Note: You'll need to create this endpoint in your FastAPI backend
        // For now, we'll simulate or you can implement it
        const response = await fetch(`${API_BASE_URL}/api/jobs/discover-and-apply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // For streaming/real-time updates, you might want to use Server-Sent Events
        // For now, we'll poll or wait for the full response
        const result = await response.json();
        handleResults(result);
        
    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
        log('💡 Make sure the FastAPI server is running and the endpoint is implemented', 'warning');
        isRunning = false;
        startBtn.disabled = false;
        stopBtn.style.display = 'none';
    }
}

function handleStop() {
    if (confirm('Are you sure you want to stop the job discovery?')) {
        isRunning = false;
        startBtn.disabled = false;
        stopBtn.style.display = 'none';
        log('⏹️ Stopped by user', 'warning');
    }
}

function handleResults(results) {
    isRunning = false;
    startBtn.disabled = false;
    stopBtn.style.display = 'none';
    resultsPanel.style.display = 'block';
    currentResults = results;
    
    // Update stats
    updateStats(results);
    
    // Update progress to 100%
    progressFill.style.width = '100%';
    progressText.textContent = '✅ Complete!';
    
    // Display results
    displayResults(results);
    
    log('✅ Job discovery and application complete!', 'success');
}

function updateStats(results) {
    const discovered = results.jobs_discovered?.length || 0;
    const filtered = results.jobs_filtered?.length || 0;
    const submitted = results.applications_submitted?.length || 0;
    const skipped = results.applications_skipped?.length || 0;
    const errors = results.errors?.length || 0;
    
    document.getElementById('jobsDiscovered').textContent = discovered;
    document.getElementById('applicationsSubmitted').textContent = submitted;
    
    const total = submitted + skipped;
    const successRate = total > 0 ? Math.round((submitted / total) * 100) : 0;
    document.getElementById('successRate').textContent = `${successRate}%`;
    document.getElementById('status').textContent = 'Complete';
}

function displayResults(results) {
    // Summary
    const summary = `
        <div>
            <div class="label">Jobs Discovered</div>
            <div class="value">${results.jobs_discovered?.length || 0}</div>
        </div>
        <div>
            <div class="label">After Filtering</div>
            <div class="value">${results.jobs_filtered?.length || 0}</div>
        </div>
        <div>
            <div class="label">Applications Submitted</div>
            <div class="value">${results.applications_submitted?.length || 0}</div>
        </div>
        <div>
            <div class="label">Jobs Skipped</div>
            <div class="value">${results.applications_skipped?.length || 0}</div>
        </div>
        <div>
            <div class="label">Errors</div>
            <div class="value">${results.errors?.length || 0}</div>
        </div>
    `;
    document.getElementById('resultsSummary').innerHTML = summary;
    
    // Applications submitted
    const applicationsList = document.getElementById('applicationsList');
    if (results.applications_submitted?.length > 0) {
        applicationsList.innerHTML = results.applications_submitted.map(app => {
            const job = app.job || {};
            return `
                <div class="job-item success">
                    <h4>${job.title || 'N/A'}</h4>
                    <div class="company">${job.company || 'N/A'}</div>
                    <div class="meta">
                        <span>📍 ${job.location || 'N/A'}</span>
                        <span>📊 Fit Score: ${app.fit_score || 'N/A'}/100</span>
                        <span>🔗 ${job.source || 'N/A'}</span>
                    </div>
                    ${job.url ? `<a href="${job.url}" target="_blank">View Job →</a>` : ''}
                </div>
            `;
        }).join('');
    } else {
        applicationsList.innerHTML = '<p>No applications submitted.</p>';
    }
    
    // Jobs skipped
    const skippedList = document.getElementById('skippedList');
    if (results.applications_skipped?.length > 0) {
        skippedList.innerHTML = results.applications_skipped.map(skip => {
            const job = skip.job || {};
            return `
                <div class="job-item warning">
                    <h4>${job.title || 'N/A'}</h4>
                    <div class="company">${job.company || 'N/A'}</div>
                    <div class="meta">
                        <span>📍 ${job.location || 'N/A'}</span>
                        <span>📊 Fit Score: ${skip.fit_score || 'N/A'}/100</span>
                        <span>⏭️ Reason: ${skip.reason || 'Low fit score'}</span>
                    </div>
                    ${job.url ? `<a href="${job.url}" target="_blank">View Job →</a>` : ''}
                </div>
            `;
        }).join('');
    } else {
        skippedList.innerHTML = '<p>No jobs skipped.</p>';
    }
    
    // Errors
    const errorsList = document.getElementById('errorsList');
    if (results.errors?.length > 0) {
        errorsList.innerHTML = results.errors.map(err => {
            const job = err.job || {};
            return `
                <div class="job-item error">
                    <h4>${job.title || 'N/A'}</h4>
                    <div class="company">${job.company || 'N/A'}</div>
                    <div class="meta">
                        <span>❌ Error: ${err.error || 'Unknown error'}</span>
                    </div>
                    ${job.url ? `<a href="${job.url}" target="_blank">View Job →</a>` : ''}
                </div>
            `;
        }).join('');
    } else {
        errorsList.innerHTML = '<p>No errors encountered.</p>';
    }
}

function switchTab(tabName) {
    // Update button states
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

function log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const className = `log-${type}`;
    logOutput.innerHTML += `<span class="${className}">[${timestamp}] ${message}</span>\n`;
    logOutput.scrollTop = logOutput.scrollHeight;
}

async function loadApplicationHistory() {
    // TODO: Implement loading past applications from Supabase
    // This would require an endpoint to fetch applications
    log('📋 Load application history (to be implemented)', 'info');
}

