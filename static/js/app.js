// RSS Feed Analyzer Dashboard JavaScript

class RSSAnalyzerApp {
    constructor() {
        this.selectedFeeds = [];
        this.analyzedArticles = [];
        this.currentIndustry = '';
        this.relevanceCriteria = [];
        
        this.initializeApp();
    }

    initializeApp() {
        this.loadIndustries();
        this.loadRelevanceCriteria();
        this.bindEvents();
    }

    bindEvents() {
        // Industry selection
        document.getElementById('industry').addEventListener('change', (e) => {
            this.currentIndustry = e.target.value;
            this.toggleCustomIndustry();
        });

        // Custom industry input
        document.getElementById('customIndustry').addEventListener('input', (e) => {
            if (e.target.value.trim()) {
                this.currentIndustry = e.target.value.trim();
                document.getElementById('industry').value = '';
            }
        });

        // Discover feeds button
        document.getElementById('discoverFeeds').addEventListener('click', () => {
            this.discoverFeeds();
        });

        // Analyze feeds button
        document.getElementById('analyzeFeeds').addEventListener('click', () => {
            this.analyzeFeeds();
        });

        // Integration type selection
        document.getElementById('integrationType').addEventListener('change', (e) => {
            this.showIntegrationConfig(e.target.value);
        });

        // Send results button
        document.getElementById('sendResults').addEventListener('click', () => {
            this.sendResults();
        });

        // Email config modal
        document.getElementById('saveEmailConfig').addEventListener('click', () => {
            this.saveEmailConfig();
        });
    }

    async loadIndustries() {
        try {
            const response = await fetch('/api/industries');
            const industries = await response.json();
            
            const select = document.getElementById('industry');
            industries.forEach(industry => {
                const option = document.createElement('option');
                option.value = industry;
                option.textContent = industry.charAt(0).toUpperCase() + industry.slice(1);
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading industries:', error);
            this.showAlert('Error loading industries', 'danger');
        }
    }

    async loadRelevanceCriteria() {
        try {
            const response = await fetch('/api/criteria');
            const criteria = await response.json();
            
            const container = document.getElementById('criteriaContainer');
            criteria.forEach(criterion => {
                const div = document.createElement('div');
                div.className = 'form-check criteria-checkbox';
                div.innerHTML = `
                    <input class="form-check-input" type="checkbox" value="${criterion.id}" id="criteria_${criterion.id}">
                    <label class="form-check-label" for="criteria_${criterion.id}">
                        <strong>${criterion.name}</strong><br>
                        <small class="text-muted">${criterion.description}</small>
                    </label>
                `;
                container.appendChild(div);
            });
        } catch (error) {
            console.error('Error loading criteria:', error);
        }
    }

    toggleCustomIndustry() {
        const customInput = document.getElementById('customIndustry');
        if (this.currentIndustry && !document.getElementById('industry').value) {
            customInput.value = this.currentIndustry;
        } else {
            customInput.value = '';
        }
    }

    async discoverFeeds() {
        if (!this.currentIndustry) {
            this.showAlert('Please select or enter an industry', 'warning');
            return;
        }

        const maxFeeds = parseInt(document.getElementById('maxFeeds').value);
        
        this.showLoading('Discovering feeds...');
        
        try {
            const response = await fetch('/api/feeds/discover', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    industry: this.currentIndustry,
                    custom_industry: document.getElementById('customIndustry').value,
                    max_feeds: maxFeeds
                })
            });

            const feeds = await response.json();
            this.displayDiscoveredFeeds(feeds);
            this.hideLoading();
            
            // Enable analyze button
            document.getElementById('analyzeFeeds').disabled = false;
            
        } catch (error) {
            console.error('Error discovering feeds:', error);
            this.showAlert('Error discovering feeds', 'danger');
            this.hideLoading();
        }
    }

    displayDiscoveredFeeds(feeds) {
        const container = document.getElementById('resultsContainer');
        container.innerHTML = `
            <h6>Discovered Feeds (${feeds.length})</h6>
            <p class="text-muted">Select feeds to analyze:</p>
        `;

        feeds.forEach((feed, index) => {
            const feedDiv = document.createElement('div');
            feedDiv.className = 'feed-item';
            feedDiv.innerHTML = `
                <div class="form-check">
                    <input class="form-check-input feed-checkbox" type="checkbox" value="${feed.url}" id="feed_${index}">
                    <label class="form-check-label" for="feed_${index}">
                        <strong>${feed.title}</strong><br>
                        <small class="text-muted">${feed.url}</small>
                    </label>
                </div>
            `;
            container.appendChild(feedDiv);
        });

        // Add select all button
        const selectAllDiv = document.createElement('div');
        selectAllDiv.className = 'mt-3';
        selectAllDiv.innerHTML = `
            <button class="btn btn-sm btn-outline-primary" id="selectAllFeeds">Select All</button>
            <button class="btn btn-sm btn-outline-secondary ms-2" id="deselectAllFeeds">Deselect All</button>
        `;
        container.appendChild(selectAllDiv);

        // Bind select all events
        document.getElementById('selectAllFeeds').addEventListener('click', () => {
            document.querySelectorAll('.feed-checkbox').forEach(checkbox => {
                checkbox.checked = true;
            });
        });

        document.getElementById('deselectAllFeeds').addEventListener('click', () => {
            document.querySelectorAll('.feed-checkbox').forEach(checkbox => {
                checkbox.checked = false;
            });
        });
    }

    async analyzeFeeds() {
        // Get selected feeds
        const selectedCheckboxes = document.querySelectorAll('.feed-checkbox:checked');
        if (selectedCheckboxes.length === 0) {
            this.showAlert('Please select at least one feed to analyze', 'warning');
            return;
        }

        this.selectedFeeds = Array.from(selectedCheckboxes).map(cb => cb.value);
        
        // Get relevance criteria
        this.relevanceCriteria = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
            .map(cb => cb.value);

        const maxArticles = parseInt(document.getElementById('maxArticles').value);
        
        this.showLoading('Analyzing feeds...');
        
        try {
            const response = await fetch('/api/feeds/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feed_urls: this.selectedFeeds,
                    max_articles: maxArticles,
                    relevance_criteria: this.relevanceCriteria,
                    industry: this.currentIndustry
                })
            });

            this.analyzedArticles = await response.json();
            this.displayAnalyzedArticles();
            this.hideLoading();
            
            // Enable send results button
            document.getElementById('sendResults').disabled = false;
            
        } catch (error) {
            console.error('Error analyzing feeds:', error);
            this.showAlert('Error analyzing feeds', 'danger');
            this.hideLoading();
        }
    }

    displayAnalyzedArticles() {
        const container = document.getElementById('resultsContainer');
        const countElement = document.getElementById('resultsCount');
        
        countElement.textContent = `${this.analyzedArticles.length} articles`;
        
        container.innerHTML = `
            <h6>Analysis Results</h6>
            <p class="text-muted">Articles ranked by relevance:</p>
        `;

        this.analyzedArticles.forEach((article, index) => {
            const score = article.relevance_score || 0;
            const scoreClass = score >= 80 ? 'high' : score >= 60 ? 'medium' : 'low';
            
            const articleDiv = document.createElement('div');
            articleDiv.className = 'article-card';
            articleDiv.innerHTML = `
                <div class="article-title">
                    <a href="${article.link}" target="_blank">${article.title}</a>
                </div>
                <div class="article-summary">${article.summary || 'No summary available'}</div>
                <div class="article-meta">
                    <strong>Source:</strong> ${article.source} | 
                    <strong>Published:</strong> ${article.published} |
                    <span class="relevance-score ${scoreClass}">Relevance: ${score.toFixed(1)}%</span>
                </div>
                ${article.analysis && !article.analysis.includes('AI analysis error') ? `<div class="article-analysis"><strong>AI Analysis:</strong> ${article.analysis}</div>` : ''}
            `;
            container.appendChild(articleDiv);
        });
    }

    showIntegrationConfig(integrationType) {
        const configDiv = document.getElementById('integrationConfig');
        configDiv.style.display = 'block';
        
        let configHTML = '';
        
        switch (integrationType) {
            case 'email':
                configHTML = `
                    <div class="integration-config">
                        <h6>Email Configuration</h6>
                        <div class="mb-3">
                            <label for="emailTo" class="form-label">To Email</label>
                            <input type="email" class="form-control" id="emailTo" required>
                        </div>
                        <div class="mb-3">
                            <label for="emailSubject" class="form-label">Subject</label>
                            <input type="text" class="form-control" id="emailSubject" value="RSS Feed Analysis Results">
                        </div>
                    </div>
                `;
                break;
            case 'slack':
                configHTML = `
                    <div class="integration-config">
                        <h6>Slack Configuration</h6>
                        <div class="mb-3">
                            <label for="slackWebhook" class="form-label">Webhook URL</label>
                            <input type="url" class="form-control" id="slackWebhook" required>
                        </div>
                        <div class="mb-3">
                            <label for="slackChannel" class="form-label">Channel (optional)</label>
                            <input type="text" class="form-control" id="slackChannel" placeholder="#general">
                        </div>
                    </div>
                `;
                break;
            case 'airtable':
                configHTML = `
                    <div class="integration-config">
                        <h6>Airtable Configuration</h6>
                        <div class="mb-3">
                            <label for="airtableApiKey" class="form-label">API Key</label>
                            <input type="password" class="form-control" id="airtableApiKey" required>
                        </div>
                        <div class="mb-3">
                            <label for="airtableBaseId" class="form-label">Base ID</label>
                            <input type="text" class="form-control" id="airtableBaseId" required>
                        </div>
                        <div class="mb-3">
                            <label for="airtableTableName" class="form-label">Table Name</label>
                            <input type="text" class="form-control" id="airtableTableName" value="RSS Articles">
                        </div>
                    </div>
                `;
                break;
            case 'notion':
                configHTML = `
                    <div class="integration-config">
                        <h6>Notion Configuration</h6>
                        <div class="mb-3">
                            <label for="notionApiKey" class="form-label">API Key</label>
                            <input type="password" class="form-control" id="notionApiKey" required>
                        </div>
                        <div class="mb-3">
                            <label for="notionDatabaseId" class="form-label">Database ID</label>
                            <input type="text" class="form-control" id="notionDatabaseId" required>
                        </div>
                    </div>
                `;
                break;
        }
        
        configDiv.innerHTML = configHTML;
    }

    async sendResults() {
        const integrationType = document.getElementById('integrationType').value;
        if (!integrationType) {
            this.showAlert('Please select an integration type', 'warning');
            return;
        }

        if (this.analyzedArticles.length === 0) {
            this.showAlert('No articles to send', 'warning');
            return;
        }

        // Get integration configuration
        const config = this.getIntegrationConfig(integrationType);
        if (!config) {
            this.showAlert('Please fill in all required configuration fields', 'warning');
            return;
        }

        this.showLoading('Sending results...');
        
        try {
            const response = await fetch('/api/integrations/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    articles: this.analyzedArticles,
                    integration_type: integrationType,
                    config: config
                })
            });

            const result = await response.json();
            this.hideLoading();
            
            if (result.success) {
                this.showAlert(result.message, 'success');
            } else {
                this.showAlert(result.error, 'danger');
            }
            
        } catch (error) {
            console.error('Error sending results:', error);
            this.showAlert('Error sending results', 'danger');
            this.hideLoading();
        }
    }

    getIntegrationConfig(integrationType) {
        switch (integrationType) {
            case 'email':
                const emailTo = document.getElementById('emailTo').value;
                const emailSubject = document.getElementById('emailSubject').value;
                if (!emailTo) return null;
                return { to_email: emailTo, subject: emailSubject };
                
            case 'slack':
                const webhook = document.getElementById('slackWebhook').value;
                const channel = document.getElementById('slackChannel').value;
                if (!webhook) return null;
                return { webhook_url: webhook, channel: channel };
                
            case 'airtable':
                const apiKey = document.getElementById('airtableApiKey').value;
                const baseId = document.getElementById('airtableBaseId').value;
                const tableName = document.getElementById('airtableTableName').value;
                if (!apiKey || !baseId) return null;
                return { api_key: apiKey, base_id: baseId, table_name: tableName };
                
            case 'notion':
                const notionApiKey = document.getElementById('notionApiKey').value;
                const databaseId = document.getElementById('notionDatabaseId').value;
                if (!notionApiKey || !databaseId) return null;
                return { api_key: notionApiKey, database_id: databaseId };
                
            default:
                return null;
        }
    }

    showLoading(message = 'Loading...') {
        const spinner = document.getElementById('loadingSpinner');
        spinner.style.display = 'block';
        spinner.querySelector('p').textContent = message;
    }

    hideLoading() {
        document.getElementById('loadingSpinner').style.display = 'none';
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of container
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RSSAnalyzerApp();
});

