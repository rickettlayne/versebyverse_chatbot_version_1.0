# versebyverse_chatbot_version_1.0

Retrieval-Augmented Generation pipeline for Verse by Verse Ministry PDF studies.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install Playwright browsers (first run only):
   ```bash
   python -m playwright install
   ```
3. Provide your OpenAI key in a `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   ```

## Usage

1. Scrape PDFs:
   ```bash
   python scraper.py
   ```
2. Process and ingest into ChromaDB:
   ```bash
   python processor.py
   ```
3. Run the chatbot:
   ```bash
   python chat.py
   ```

## Tests

Run the lightweight test suite:

```bash
pytest -q
```
