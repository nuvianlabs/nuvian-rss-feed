# RSS Feed Analyzer Dashboard

A comprehensive RSS feed analysis tool that uses AI to analyze and rank articles from multiple RSS feeds based on relevance to your industry and selected criteria.

## Features

- **Multi-Industry Support**: Pre-configured feeds for Technology, Finance, Healthcare, Marketing, Business, and Science
- **Custom Industry Support**: Add your own industry and discover relevant feeds
- **AI-Powered Analysis**: Uses OpenAI GPT to analyze article relevance and provide insights
- **Flexible Relevance Criteria**: Choose from multiple relevance criteria like trending topics, innovation focus, expert analysis, etc.
- **Multiple Integrations**: Send results to Email, Slack, Airtable, or Notion
- **Modern Dashboard**: Clean, responsive web interface

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd nuvian-rss-feed
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   Edit `.env` and add your API keys:
   - `OPENAI_API_KEY`: Your OpenAI API key for AI analysis
   - `SMTP_USERNAME` and `SMTP_PASSWORD`: For email integration
   - Other optional configurations

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and go to `http://localhost:5000`

## Usage

### 1. Configure Your Analysis
- Select an industry from the dropdown or enter a custom industry
- Set the maximum number of feeds to analyze (1-50)
- Set the maximum number of articles in the final output (1-100)
- Choose relevance criteria that matter to you

### 2. Discover Feeds
- Click "Discover Feeds" to find RSS feeds relevant to your industry
- Select the feeds you want to analyze
- Use "Select All" or "Deselect All" for convenience

### 3. Analyze Content
- Click "Analyze Feeds" to process the selected feeds
- The AI will analyze each article and score them based on relevance
- Results are ranked by relevance score with AI insights

### 4. Send Results
- Choose an integration type (Email, Slack, Airtable, or Notion)
- Configure the integration settings
- Click "Send Results" to deliver the analyzed articles

## Relevance Criteria

The system supports multiple relevance criteria:

- **Content Relevance**: How closely the content matches your industry focus
- **Recency**: How recent the article is (newer is better)
- **Source Authority**: Credibility and reputation of the source
- **Engagement Potential**: Likelihood to generate discussion or interest
- **Trending Topics**: Articles covering currently trending topics
- **Expert Analysis**: Articles with expert opinions or analysis
- **Innovation Focus**: Articles about new technologies or methodologies
- **Market Impact**: Potential impact on markets or business

## Integrations

### Email
- Send formatted HTML emails with article summaries and analysis
- Configure SMTP settings in environment variables

### Slack
- Send results to Slack channels using webhooks
- Configure webhook URL and optional channel

### Airtable
- Create records in Airtable with article data
- Requires API key, base ID, and table name

### Notion
- Create pages in Notion databases
- Requires API key and database ID

## API Endpoints

- `GET /api/industries` - Get available industries
- `POST /api/feeds/discover` - Discover feeds for an industry
- `POST /api/feeds/analyze` - Analyze RSS feeds and return relevant articles
- `POST /api/integrations/send` - Send articles to external services
- `GET /api/criteria` - Get available relevance criteria

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for AI analysis
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: For email integration
- `REDIS_URL`: For background task processing (optional)

### Industry Feed Configuration

The system comes with pre-configured feeds for common industries. You can modify the `industry_feeds` dictionary in `industry_feeds.py` to add more feeds or industries.

## Development

### Project Structure
```
nuvian-rss-feed/
├── app.py                 # Main Flask application
├── rss_analyzer.py       # AI analysis logic
├── industry_feeds.py     # Industry-specific feed management
├── integrations.py       # External service integrations
├── templates/
│   └── index.html        # Dashboard HTML
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── requirements.txt       # Python dependencies
└── README.md            # This file
```

### Adding New Industries

1. Add the industry to the `industry_feeds` dictionary in `industry_feeds.py`
2. Add relevant RSS feeds for that industry
3. The system will automatically include it in the industry dropdown

### Adding New Integrations

1. Add the integration logic to `integrations.py`
2. Add the integration type to the frontend dropdown
3. Add configuration fields in the JavaScript `showIntegrationConfig` method

## Troubleshooting

### Common Issues

1. **OpenAI API errors**: Ensure your API key is valid and has sufficient credits
2. **Email sending fails**: Check SMTP credentials and ensure app passwords are used for Gmail
3. **Feed parsing errors**: Some RSS feeds may be malformed or inaccessible
4. **Integration failures**: Verify API keys and configuration for external services

### Debug Mode

Run with debug mode enabled:
```bash
FLASK_DEBUG=True python app.py
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

