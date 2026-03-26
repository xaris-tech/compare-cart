# E-commerce Growth Agent 🚀

Automated competitor monitoring and marketing content generation for Shopee & Lazada.

## Features

- **Competitor Scraping**: Extract product data from Shopee and Lazada
- **AI-Powered Marketing**: Generate SEO copy, ad headlines, keywords, and image prompts using Claude 3.5 Sonnet
- **Dashboard**: Streamlit UI for easy input and output

## Installation

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy the example env file:
```bash
cp .env.example .env
```

2. Add your OpenRouter API key in `.env`:
```
OPENROUTER_API_KEY=your_key_here
```
Get free API key at https://openrouter.ai

## Usage

```bash
streamlit run app.py
```

## How It Works

1. **Input**: Enter a keyword (e.g., "wireless earbuds") and select platform
2. **Scrape**: Agent extracts competitor products with prices, sales, ratings
3. **Generate**: Claude AI analyzes the data and creates:
   - SEO-optimized titles & descriptions
   - Ad headlines for Google/Facebook/Instagram
   - Keyword suggestions
   - AI image generation prompts (Midjourney/DALL-E)
4. **Download**: Export marketing pack as JSON

## Project Structure

```
.
├── app.py                 # Streamlit dashboard
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── scrapers/              # Web scrapers
│   ├── shopee.py
│   └── lazada.py
├── agent/                 # Marketing AI agent
│   └── marketing_agent.py
└── outputs/               # Generated files
```

## Notes

- Without an API key, the agent uses mock data for demonstration
- Scraping requires Chrome browser installed
- Respect platform terms of service when scraping
