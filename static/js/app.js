// Job Application Tracker - Frontend JavaScript
class JobTrackerApp {
    constructor() {
        this.currentJobs = [];
        this.allJobs = [];
        this.currentSeason = null;
        this.selectedSeasonId = null;
        this.jobStatuses = [];
        this.statusChart = null;
        this.timelineChart = null;
        
        this.init();
    }
    
    async init() {
        await this.loadJobStatuses();
        await this.loadInitialData();
        this.setupEventListeners();
        this.setupCharts();
    }
    
    // API Helper Methods
    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(`/api${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            this.showToast('error', 'Error', error.message);
            throw error;
        }
    }
    
    // Data Loading Methods
    async loadJobStatuses() {
        try {
            const response = await this.apiCall('/job-statuses');
            this.jobStatuses = response.data;
            this.populateStatusSelects();
        } catch (error) {
            console.error('Failed to load job statuses:', error);
        }
    }
    
    async loadInitialData() {
        await Promise.all([
            this.loadActiveSeason(),
            this.loadAllSeasons(),
            this.loadJobs()
        ]);
    }
    
    async loadActiveSeason() {
        try {
            const response = await this.apiCall('/seasons/active');
            if (response.data) {
                this.currentSeason = response.data.season;
                this.selectedSeasonId = response.data.season.id;
                this.updateCurrentSeasonDisplay(response.data);
                this.updateStatistics(response.data.stats);
            } else {
                this.showNoSeasonWarning();
            }
        } catch (error) {
            console.error('Failed to load active season:', error);
        }
    }
    
    async loadAllSeasons() {
        try {
            const response = await this.apiCall('/seasons');
            this.updateSeasonsDisplay(response.data, this.selectedSeasonId);
        } catch (error) {
            console.error('Failed to load seasons:', error);
        }
    }
    
    async loadJobs() {
        try {
            // Load jobs for the selected season (or active season if none selected)
            const seasonParam = this.selectedSeasonId ? `?season_id=${this.selectedSeasonId}` : '';
            const response = await this.apiCall(`/jobs${seasonParam}`);
            this.allJobs = response.data;
            this.currentJobs = [...this.allJobs];
            this.updateJobsTable();
            this.updateCharts();
        } catch (error) {
            console.error('Failed to load jobs:', error);
        }
    }
    
    // Display Update Methods
    updateCurrentSeasonDisplay(data) {
        const container = document.getElementById('currentSeason');
        const { season, stats } = data;
        
        const statusBadge = season.is_active 
            ? '<span style="background: var(--success-color); color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; margin-left: 0.5rem;">Active</span>'
            : '<span style="background: var(--gray-500); color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; margin-left: 0.5rem;">Ended</span>';
        
        const returnButton = !season.is_active && this.currentSeason 
            ? `<button class="btn btn-outline" style="width: 100%; margin-top: 1rem; font-size: 0.85rem;" onclick="app.returnToActiveSeason()">
                <i class="fas fa-arrow-left"></i> Return to Active Season
               </button>`
            : '';
        
        container.innerHTML = `
            <div class="season-name">
                ${season.name}
                ${statusBadge}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;">
                Started: ${this.formatDate(season.start_date)}
                ${season.end_date ? `<br>Ended: ${this.formatDate(season.end_date)}` : ''}
            </div>
            <div class="season-stats">
                <div class="stat-item">
                    <span class="stat-value">${stats.total || 0}</span>
                    <span class="stat-label">Total Jobs</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${stats.active || 0}</span>
                    <span class="stat-label">Active</span>
                </div>
            </div>
            ${returnButton}
        `;
    }
    
    showNoSeasonWarning() {
        const container = document.getElementById('currentSeason');
        container.innerHTML = `
            <div style="text-align: center; padding: 1rem; color: var(--text-secondary);">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem; color: var(--warning-color);"></i>
                <p>No active season found</p>
                <button class="btn btn-primary" onclick="app.openModal('seasonModal')" style="margin-top: 1rem;">
                    Create Season
                </button>
            </div>
        `;
    }
    
    updateSeasonsDisplay(seasons, selectedSeasonId = null) {
        const container = document.getElementById('allSeasons');
        
        if (seasons.length === 0) {
            container.innerHTML = '<div class="loading">No seasons found</div>';
            return;
        }
        
        container.innerHTML = seasons.map(season => {
            const isSelected = selectedSeasonId ? season.id === selectedSeasonId : season.is_active;
            const isEnded = season.end_date !== null;
            const classes = [
                'season-item',
                isSelected ? 'active' : '',
                isEnded && !isSelected ? 'ended' : ''
            ].filter(Boolean).join(' ');
            
            return `
                <div class="${classes}" onclick="app.selectSeason(${season.id})">
                    <div class="season-item-name">${season.name}</div>
                    <div class="season-item-date">
                        ${this.formatDate(season.start_date)}
                        ${season.end_date ? ` - ${this.formatDate(season.end_date)}` : ' (Active)'}
                    </div>
                    ${isSelected ? '<div style="font-size: 0.8rem; color: var(--primary-color); margin-top: 0.25rem;">Currently Viewing</div>' : ''}
                </div>
            `;
        }).join('');
    }
    
    updateStatistics(stats) {
        const container = document.getElementById('statsGrid');
        
        const statCards = [
            {
                title: 'Total Applications',
                value: stats.total || 0,
                icon: 'fas fa-briefcase',
                iconClass: 'icon-blue',
                change: null
            },
            {
                title: 'Active Applications',
                value: stats.active || 0,
                icon: 'fas fa-clock',
                iconClass: 'icon-yellow',
                change: null
            },
            {
                title: 'Interviews',
                value: (stats.interviews || 0),
                icon: 'fas fa-users',
                iconClass: 'icon-green',
                change: null
            },
            {
                title: 'Offers',
                value: stats.offers || 0,
                icon: 'fas fa-trophy',
                iconClass: 'icon-green',
                change: null
            },
            {
                title: 'Success Rate',
                value: stats.total > 0 ? `${Math.round(((stats.offers || 0) / stats.total) * 100)}%` : '0%',
                icon: 'fas fa-chart-line',
                iconClass: 'icon-cyan',
                change: null
            }
        ];
        
        container.innerHTML = statCards.map(card => `
            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-card-title">${card.title}</div>
                    <div class="stat-card-icon ${card.iconClass}">
                        <i class="${card.icon}"></i>
                    </div>
                </div>
                <div class="stat-card-value">${card.value}</div>
                ${card.change ? `<div class="stat-card-change ${card.change > 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${card.change > 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(card.change)}%
                </div>` : ''}
            </div>
        `).join('');
    }
    
    updateJobsTable() {
        const tbody = document.getElementById('jobsTableBody');
        
        if (this.currentJobs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; color: var(--text-secondary); padding: 3rem;">
                        <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                        <div>No job applications found</div>
                        <button class="btn btn-primary" onclick="app.openModal('jobModal')" style="margin-top: 1rem;">
                            Add Your First Job
                        </button>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = this.currentJobs.map(job => `
            <tr>
                <td>
                    <div class="company-info">
                        <div class="company-logo">
                            ${job.company_name.charAt(0).toUpperCase()}
                        </div>
                        <div class="company-details">
                            <h4>${job.company_name}</h4>
                            ${job.company_website ? `<p><a href="${job.company_website}" target="_blank">Website</a></p>` : ''}
                        </div>
                    </div>
                </td>
                <td>
                    <strong>${job.role}</strong>
                    ${job.source ? `<br><small style="color: var(--text-secondary);">via ${job.source}</small>` : ''}
                </td>
                <td>
                    <span class="status-badge status-${this.getStatusClass(job.current_status)}">
                        ${job.current_status}
                    </span>
                </td>
                <td>${job.applied_date ? this.formatDate(job.applied_date) : 'N/A'}</td>
                <td>${job.applied_date ? this.getDaysSince(job.applied_date) + ' days' : 'N/A'}</td>
                <td>${job.source || 'N/A'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-icon btn-view" onclick="app.viewJobDetails(${job.id})" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-icon btn-edit" onclick="app.openStatusModal(${job.id})" title="Update Status">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon btn-delete" onclick="app.deleteJob(${job.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    // Chart Methods
    setupCharts() {
        this.setupStatusChart();
        this.setupTimelineChart();
    }
    
    setupStatusChart() {
        const ctx = document.getElementById('statusChart');
        if (!ctx) return;
        
        this.statusChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6',
                        '#ec4899', '#22c55e', '#ef4444', '#6b7280', '#f59e0b'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    setupTimelineChart() {
        const ctx = document.getElementById('timelineChart');
        if (!ctx) return;
        
        this.timelineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Applications',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    updateCharts() {
        this.updateStatusChart();
        this.updateTimelineChart();
    }
    
    updateStatusChart() {
        if (!this.statusChart) return;
        
        const statusCounts = {};
        this.currentJobs.forEach(job => {
            statusCounts[job.current_status] = (statusCounts[job.current_status] || 0) + 1;
        });
        
        const labels = Object.keys(statusCounts);
        const data = Object.values(statusCounts);
        
        this.statusChart.data.labels = labels;
        this.statusChart.data.datasets[0].data = data;
        this.statusChart.update();
    }
    
    updateTimelineChart() {
        if (!this.timelineChart) return;
        
        // Group jobs by applied date
        const dateCounts = {};
        this.currentJobs.forEach(job => {
            if (job.applied_date) {
                const date = job.applied_date.split('T')[0];
                dateCounts[date] = (dateCounts[date] || 0) + 1;
            }
        });
        
        const sortedDates = Object.keys(dateCounts).sort();
        const labels = sortedDates.map(date => this.formatDate(date));
        const data = sortedDates.map(date => dateCounts[date]);
        
        this.timelineChart.data.labels = labels;
        this.timelineChart.data.datasets[0].data = data;
        this.timelineChart.update();
    }
    
    // Modal Methods
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            
            // Reset forms
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
                // Clear job ID for new jobs
                const jobIdInput = form.querySelector('#jobId');
                if (jobIdInput) {
                    jobIdInput.value = '';
                }
            }
            
            // Set current date for job applications
            if (modalId === 'jobModal') {
                const appliedDateInput = document.getElementById('appliedDate');
                if (appliedDateInput) {
                    appliedDateInput.value = new Date().toISOString().split('T')[0];
                }
            }
        }
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
        }
    }
    
    // Season Methods
    async createSeason(event) {
        event.preventDefault();
        
        const name = document.getElementById('seasonName').value.trim();
        if (!name) {
            this.showToast('error', 'Error', 'Season name is required');
            return;
        }
        
        try {
            const response = await this.apiCall('/seasons', {
                method: 'POST',
                body: JSON.stringify({ name })
            });
            
            this.showToast('success', 'Success', response.message);
            this.closeModal('seasonModal');
            await this.loadInitialData();
        } catch (error) {
            // Error already handled in apiCall
        }
    }
    
    async endCurrentSeason() {
        if (!confirm('Are you sure you want to end the current season?')) {
            return;
        }
        
        try {
            const response = await this.apiCall('/seasons/end', {
                method: 'POST'
            });
            
            this.showToast('success', 'Success', response.message);
            await this.loadInitialData();
        } catch (error) {
            // Error already handled in apiCall
        }
    }
    
    async selectSeason(seasonId) {
        try {
            // Don't switch if already viewing this season
            if (this.selectedSeasonId === seasonId) {
                return;
            }
            
            // Load jobs for the selected season
            const response = await this.apiCall(`/jobs?season_id=${seasonId}`);
            this.allJobs = response.data;
            this.currentJobs = [...this.allJobs];
            
            // Update selected season tracking
            this.selectedSeasonId = seasonId;
            
            // Clear any active filters when switching seasons
            this.clearFilters();
            
            // Update the jobs table
            this.updateJobsTable();
            
            // Update charts with new data
            this.updateCharts();
            
            // Load season info and stats
            const seasons = await this.apiCall('/seasons');
            const selectedSeason = seasons.data.find(s => s.id === seasonId);
            
            if (selectedSeason) {
                // Calculate stats for this season
                const stats = this.calculateSeasonStats(this.allJobs);
                
                // Update current season display
                this.updateCurrentSeasonDisplay({
                    season: selectedSeason,
                    stats: stats
                });
                
                // Update statistics cards
                this.updateStatistics(stats);
                
                // Update seasons display to show selection
                this.updateSeasonsDisplay(seasons.data, seasonId);
                
                // Show success message
                const isActive = selectedSeason.is_active;
                const statusText = isActive ? '(Active)' : '(Ended)';
                this.showToast('success', 'Season Switched', `Now viewing: ${selectedSeason.name} ${statusText}`);
            }
        } catch (error) {
            this.showToast('error', 'Error', 'Failed to switch season');
            console.error('Season switch error:', error);
        }
    }
    
    async returnToActiveSeason() {
        if (this.currentSeason && this.currentSeason.id) {
            await this.selectSeason(this.currentSeason.id);
        }
    }
    
    // Job Methods
    async saveJob(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const jobData = {
            role: document.getElementById('jobRole').value.trim(),
            company_name: document.getElementById('companyName').value.trim(),
            status: document.getElementById('jobStatus').value,
            applied_date: document.getElementById('appliedDate').value,
            source: document.getElementById('jobSource').value.trim(),
            company_website: document.getElementById('companyWebsite').value.trim(),
            job_description: document.getElementById('jobDescription').value.trim(),
            resume_sent: document.getElementById('resumeSent').value.trim()
        };
        
        // Remove empty strings
        Object.keys(jobData).forEach(key => {
            if (jobData[key] === '') {
                delete jobData[key];
            }
        });
        
        try {
            const response = await this.apiCall('/jobs', {
                method: 'POST',
                body: JSON.stringify(jobData)
            });
            
            this.showToast('success', 'Success', response.message);
            this.closeModal('jobModal');
            await this.loadJobs();
            await this.loadActiveSeason(); // Refresh stats
        } catch (error) {
            // Error already handled in apiCall
        }
    }
    
    async viewJobDetails(jobId) {
        try {
            const response = await this.apiCall(`/jobs/${jobId}`);
            const job = response.data;
            
            const modal = document.getElementById('jobDetailsModal');
            const content = document.getElementById('jobDetailsContent');
            
            content.innerHTML = `
                <div class="job-details">
                    <div class="job-details-header">
                        <div class="job-details-info">
                            <h3>${job.role}</h3>
                            <p>${job.company_name}</p>
                        </div>
                        <div class="status-badge status-${this.getStatusClass(job.current_status)}">
                            ${job.current_status}
                        </div>
                    </div>
                    
                    <div class="job-details-grid">
                        <div class="detail-group">
                            <h4>Applied Date</h4>
                            <p>${job.applied_date ? this.formatDate(job.applied_date) : 'N/A'}</p>
                        </div>
                        <div class="detail-group">
                            <h4>Days Since Applied</h4>
                            <p>${job.applied_date ? this.getDaysSince(job.applied_date) + ' days' : 'N/A'}</p>
                        </div>
                        <div class="detail-group">
                            <h4>Source</h4>
                            <p>${job.source || 'N/A'}</p>
                        </div>
                        <div class="detail-group">
                            <h4>Company Website</h4>
                            <p>${job.company_website ? `<a href="${job.company_website}" target="_blank">${job.company_website}</a>` : 'N/A'}</p>
                        </div>
                    </div>
                    
                    ${job.job_description ? `
                        <div class="detail-group">
                            <h4>Job Description</h4>
                            <p>${job.job_description}</p>
                        </div>
                    ` : ''}
                    
                    ${job.resume_sent ? `
                        <div class="detail-group">
                            <h4>Resume Link</h4>
                            <p><a href="${job.resume_sent}" target="_blank">View Resume</a></p>
                        </div>
                    ` : ''}
                    
                    <div class="form-actions">
                        <button class="btn btn-outline" onclick="app.closeModal('jobDetailsModal')">Close</button>
                        <button class="btn btn-primary" onclick="app.openStatusModal(${job.id}); app.closeModal('jobDetailsModal');">Update Status</button>
                    </div>
                </div>
            `;
            
            this.openModal('jobDetailsModal');
        } catch (error) {
            // Error already handled in apiCall
        }
    }
    
    openStatusModal(jobId) {
        const job = this.currentJobs.find(j => j.id === jobId);
        if (!job) {
            this.showToast('error', 'Error', 'Job not found');
            return;
        }
        
        document.getElementById('statusJobId').value = jobId;
        document.getElementById('newStatus').value = job.current_status;
        
        const jobInfo = document.getElementById('currentJobInfo');
        jobInfo.innerHTML = `
            <h4>${job.role} at ${job.company_name}</h4>
            <p>Current Status: <span class="status-badge status-${this.getStatusClass(job.current_status)}">${job.current_status}</span></p>
            <p>Applied: ${job.applied_date ? this.formatDate(job.applied_date) : 'N/A'}</p>
        `;
        
        this.openModal('statusModal');
    }
    
    async updateJobStatus(event) {
        event.preventDefault();
        
        const jobId = document.getElementById('statusJobId').value;
        const status = document.getElementById('newStatus').value;
        
        try {
            const response = await this.apiCall(`/jobs/${jobId}/status`, {
                method: 'PUT',
                body: JSON.stringify({ status })
            });
            
            this.showToast('success', 'Success', response.message);
            this.closeModal('statusModal');
            await this.loadJobs();
            await this.loadActiveSeason(); // Refresh stats
        } catch (error) {
            // Error already handled in apiCall
        }
    }
    
    async deleteJob(jobId) {
        const job = this.currentJobs.find(j => j.id === jobId);
        if (!job) {
            this.showToast('error', 'Error', 'Job not found');
            return;
        }
        
        if (!confirm(`Are you sure you want to delete the application for ${job.role} at ${job.company_name}?`)) {
            return;
        }
        
        try {
            const response = await this.apiCall(`/jobs/${jobId}`, {
                method: 'DELETE'
            });
            
            this.showToast('success', 'Success', response.message);
            await this.loadJobs();
            await this.loadActiveSeason(); // Refresh stats
        } catch (error) {
            // Error already handled in apiCall
        }
    }
    
    // Search and Filter Methods
    async applySearch() {
        const searchTerm = document.getElementById('searchInput').value.trim();
        
        if (!searchTerm) {
            this.currentJobs = [...this.allJobs];
            this.updateJobsTable();
            return;
        }
        
        try {
            const response = await this.apiCall(`/jobs/search?q=${encodeURIComponent(searchTerm)}`);
            this.currentJobs = response.data;
            this.updateJobsTable();
        } catch (error) {
            // Error already handled in apiCall
        }
    }
    
    async applyFilters() {
        const status = document.getElementById('statusFilter').value;
        
        if (!status) {
            this.currentJobs = [...this.allJobs];
            this.updateJobsTable();
            return;
        }
        
        try {
            const response = await this.apiCall(`/jobs/filter?status=${encodeURIComponent(status)}`);
            this.currentJobs = response.data;
            this.updateJobsTable();
        } catch (error) {
            // Error already handled in apiCall
        }
    }
    
    clearFilters() {
        document.getElementById('searchInput').value = '';
        document.getElementById('statusFilter').value = '';
        this.currentJobs = [...this.allJobs];
        this.updateJobsTable();
    }
    
    async refreshData() {
        await this.loadInitialData();
        this.showToast('success', 'Success', 'Data refreshed successfully');
    }
    
    // Helper Methods
    calculateSeasonStats(jobs) {
        const stats = {
            total: jobs.length,
            active: 0,
            interviews: 0,
            offers: 0,
            rejected: 0
        };
        
        jobs.forEach(job => {
            const status = job.current_status.toLowerCase();
            
            // Count active applications (not rejected, withdrawn, or offer)
            if (!['rejected', 'withdrawn', 'offer'].includes(status)) {
                stats.active++;
            }
            
            // Count interviews (phone screen, technical, onsite, final)
            if (['phone screen', 'technical interview', 'onsite interview', 'final interview'].includes(status)) {
                stats.interviews++;
            }
            
            // Count offers
            if (status === 'offer') {
                stats.offers++;
            }
            
            // Count rejections
            if (status === 'rejected') {
                stats.rejected++;
            }
        });
        
        return stats;
    }
    
    populateStatusSelects() {
        const selects = ['jobStatus', 'statusFilter', 'newStatus'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                // Clear existing options (except for filter which has "All Statuses")
                if (selectId === 'statusFilter') {
                    // Keep the first option
                    while (select.children.length > 1) {
                        select.removeChild(select.lastChild);
                    }
                } else {
                    select.innerHTML = '';
                }
                
                this.jobStatuses.forEach(status => {
                    const option = document.createElement('option');
                    option.value = status;
                    option.textContent = status;
                    select.appendChild(option);
                });
            }
        });
    }
    
    getStatusClass(status) {
        return status.toLowerCase().replace(/\s+/g, '-');
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
    
    getDaysSince(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    }
    
    setupEventListeners() {
        // Modal close on background click
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('modal')) {
                this.closeModal(event.target.id);
            }
        });
        
        // Search on Enter key
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    this.applySearch();
                }
            });
        }
        
        // Auto-search with debounce
        let searchTimeout;
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.applySearch();
                }, 500);
            });
        }
    }
    
    // Toast Notification Methods
    showToast(type, title, message) {
        const container = document.getElementById('toastContainer');
        const toastId = 'toast-' + Date.now();
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.id = toastId;
        toast.innerHTML = `
            <div class="toast-header">
                <div class="toast-title">${title}</div>
                <button class="toast-close" onclick="app.closeToast('${toastId}')">&times;</button>
            </div>
            <div class="toast-message">${message}</div>
        `;
        
        container.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.closeToast(toastId);
        }, 5000);
    }
    
    closeToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.remove();
        }
    }
}

// Global functions for HTML onclick handlers
let app;

function openModal(modalId) {
    app.openModal(modalId);
}

function closeModal(modalId) {
    app.closeModal(modalId);
}

function createSeason(event) {
    app.createSeason(event);
}

function saveJob(event) {
    app.saveJob(event);
}

function updateJobStatus(event) {
    app.updateJobStatus(event);
}

function applyFilters() {
    app.applyFilters();
}

function applySearch() {
    app.applySearch();
}

function clearFilters() {
    app.clearFilters();
}

function refreshData() {
    app.refreshData();
}

function returnToActiveSeason() {
    app.returnToActiveSeason();
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app = new JobTrackerApp();
});
