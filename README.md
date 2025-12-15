# Personal Brand Content Generator

A powerful GenAI application that transforms long-form content into platform-specific social media posts using LangChain and LLMs.

## Features

- 🤖 **AI-Powered Content Generation** using OpenAI GPT-5 mini or Anthropic Claude 3.5 Haiku
- 📱 **Multi-Platform Support**: LinkedIn, Twitter/X, Instagram, Facebook
- 🚀 **Instant Posting** directly to social media platforms
- 📅 **Scheduled Posting** for optimal timing
- 📋 **Copy & Download** options for manual posting
- 🎨 **Clean Streamlit UI** with tabs and organized layout

## Tech Stack

- **Frontend**: Streamlit
- **Orchestration**: LangChain
- **LLM**: OpenAI GPT-5 mini / Anthropic Claude 3.5 Haiku
- **Language**: Python 3.11+
- **Social Media Integration**: MCP Social Media Manager

## Installation

1. **Clone the repository**
```bash
cd personal-brand-content-generator
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows PowerShell
.\venv\Scripts\activate.bat
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy the example file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env and add your API keys
```

5. **Install MCP Social Media Manager Extension (Optional)**
   - Open VSCode
   - Search for "Social Media Manager - AI-Powered Multi-Platform Posting"
   - Install the extension (`epochcore.social-media-manager`)

## Configuration

Edit the `.env` file with your credentials:

```env
# Choose your LLM provider
OPENAI_API_KEY=your_openai_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_key_here

DEFAULT_LLM_PROVIDER=openai  # or "anthropic"
```

## Usage

1. **Start the application**
```bash
streamlit run app.py
```

2. **Generate content**
   - Paste your long-form content (blog post, article, newsletter)
   - Select target platforms
   - Click "Generate Content"

3. **Post or schedule**
   - **Instant Post**: Click "Post Instantly" to publish immediately
   - **Schedule**: Set date/time for future posting
   - **Copy**: Copy content to clipboard for manual posting
   - **Download**: Save all content as a text file

## Project Structure

```
content-generator/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── src/
│   ├── prompts.py            # Platform-specific prompt templates
│   └── llm_orchestrator.py   # LangChain content generation logic
│
├── utils/
│   ├── config.py             # Configuration management
│   ├── formatters.py         # Content formatting utilities
│   └── social_poster.py      # Social media posting integration
│
└── examples/
    └── sample_content.txt    # Example content for testing
```

## Platform-Specific Rules

### LinkedIn (3000 char limit)
- Professional tone
- 2-3 paragraphs
- Industry hashtags (3-5)
- Call-to-action

### Twitter/X (280 char per tweet)
- Thread format (5-7 tweets)
- Punchy, concise
- Relevant hashtags (2-3)
- Hook in first tweet

### Instagram (2200 char caption)
- Storytelling approach
- Line breaks for readability
- Emoji integration
- Many hashtags (20-30)

### Facebook (optimal: 100-250 chars)
- Conversational tone
- Question to drive engagement
- Moderate hashtags (3-5)

## Development

### Adding New Platforms
1. Update `SUPPORTED_PLATFORMS` in `utils/social_poster.py`
2. Add platform-specific prompt in `src/prompts.py`
3. Update character limits in `.env` and `utils/config.py`

### Error Handling
All API calls are wrapped in try/except blocks to prevent UI crashes.

## Troubleshooting

**Issue**: "API key is missing"
- **Solution**: Check your `.env` file and ensure the correct API key is set

**Issue**: "Platform not supported"
- **Solution**: Verify platform name is one of: linkedin, twitter, instagram, facebook

**Issue**: Scheduled post failed
- **Solution**: Ensure scheduled time is in the future and MCP extension is installed

## License

MIT License

## Contributors

Built for COSC41000 Final Project
