# Quick Start Guide

Get your Verse by Verse RAG Chatbot running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation Steps

### 1. Clone and Navigate
```bash
git clone https://github.com/rickettlayne/versebyverse_chatbot_version_1.0.git
cd versebyverse_chatbot_version_1.0
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Use your favorite text editor:
nano .env
# or
vim .env
# or
code .env  # if you have VS Code
```

Your `.env` file should look like:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### 5. Run the Application
```bash
python main.py
```

## First Run

The first time you run the application, it will:

1. **Scrape PDFs** from Verse by Verse Ministry (may take a few minutes)
2. **Process PDFs** and extract text
3. **Create embeddings** and build vector store (uses OpenAI API)
4. **Start interactive mode** where you can ask questions

This setup process only happens once. Subsequent runs will use the cached data.

## Example Questions

Once the chatbot is running, try asking:

- "What is the main theme of Genesis?"
- "Tell me about the creation account"
- "What does the book of Romans teach about faith?"
- "Explain the significance of the covenant in the Old Testament"

## Tips

- **First run takes time**: PDF scraping and processing can take 10-20 minutes depending on the number of PDFs
- **Be patient**: The vector store creation uses OpenAI API and processes all content
- **Costs**: Embedding creation and queries use OpenAI credits (typically $1-5 for full setup)
- **Re-scrape**: Use `python main.py --rescrape` to download fresh PDFs and rebuild

## Troubleshooting

### "No module named..."
```bash
# Make sure you activated the virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### "OPENAI_API_KEY not set"
```bash
# Make sure .env file exists and has your API key
cat .env  # Check the file
# Edit if needed
nano .env
```

### "No PDFs downloaded"
- Check your internet connection
- Verify the target URLs are accessible
- The website may have changed - check the URLs in `src/utils/config.py`

### Vector store errors
```bash
# Delete and rebuild
rm -rf data/vectorstore
python main.py
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [example_usage.py](example_usage.py) for programmatic usage
- Customize settings in `.env` file

## Support

For issues or questions, please open an issue on GitHub.

## Have Fun!

You now have a powerful Bible study assistant powered by AI! Ask questions and explore the materials from Verse by Verse Ministry.
