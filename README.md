# RAG Chatbot for Hikvision and Satel Products

A comprehensive RAG (Retrieval-Augmented Generation) chatbot application for querying Hikvision and Satel product information, with an integrated technician agent.

## Features

- **Product Queries**: Ask questions about Hikvision and Satel products
- **Product Search**: Search and compare product characteristics
- **Technician Agent**: Query technician information via integrated agent
- **RAG-based**: Uses FAISS vector stores and LangChain for semantic search
- **Multi-source**: Supports both CSV and PDF data sources
- **Web Scraping**: Scripts to collect product data from Hikvision and Satel websites

## Project Structure

```
Rag_chatbot/
├── app.py                      # Main Streamlit application
├── config/                     # Configuration files
│   ├── __init__.py
│   └── settings.py            # Application settings
├── src/                        # Source code
│   ├── agents/                # Agent modules
│   │   ├── __init__.py
│   │   └── technician_agent.py
│   ├── models/                # LLM and embedding models
│   │   ├── __init__.py
│   │   ├── llm.py
│   │   └── embeddings.py
│   ├── retrievers/            # RAG retrieval functions
│   │   ├── __init__.py
│   │   ├── index_creation.py
│   │   ├── qa_chains.py
│   │   └── product_analysis.py
│   ├── ui/                    # UI components
│   │   ├── __init__.py
│   │   ├── styles.py
│   │   └── components.py
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── session_state.py
│       └── search.py
├── scripts/                    # Web scraping scripts
│   ├── __init__.py
│   ├── hikvision_scraper.py   # Hikvision product scraper
│   ├── satel_scraper.py       # Satel product scraper
│   └── README.md              # Scraping scripts documentation
├── data/                      # Data files (CSV files)
│   ├── my_hikvision_data.csv
│   └── my_satel_data.csv
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── SETUP_INSTRUCTIONS.md     # Setup guide
├── CREDENTIALS_SETUP.md      # Google Drive credentials guide
├── MIGRATION_GUIDE.md        # Migration instructions
└── GITHUB_README.md          # GitHub preparation guide
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Rag_chatbot
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Place your data files in the `data/` directory:
   - `my_hikvision_data.csv` - Hikvision product data
   - `my_satel_data.csv` - Satel product data
   
   Or use the web scraping scripts in `scripts/` to collect data:
   ```bash
   python scripts/hikvision_scraper.py
   python scripts/satel_scraper.py
   ```

5. **Setup Google Drive API credentials** (for technician agent):
   - Download `client_secrets.json` from Google Cloud Console
   - Place it in the **project root directory** (same folder as `app.py`)
   - See `CREDENTIALS_SETUP.md` for detailed instructions

6. Configure API keys in `config/settings.py`:
   - Set your `OPENAI_API_KEY` (or Groq API key)
   - Configure `OPENAI_API_BASE` if using Groq

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Features by Category

### Technicien
- Query technician information using the integrated agent
- Chat history is maintained during the session
- Requires Google Drive API credentials (see `CREDENTIALS_SETUP.md`)

### Hikvision Product
- **Ask about an item**: Search for products and ask questions about specific items
- **Search about caractéristiques**: Search products by characteristics and compare them

### Satel Product
- **Ask about an item**: Search for products and ask questions about specific items
- **Search about caractéristiques**: Search products by characteristics and compare them

## Configuration

Edit `config/settings.py` to customize:
- API keys and endpoints
- Model parameters (temperature, chunk size, etc.)
- Data file paths
- Retrieval parameters (k values for retrievers)

## Dependencies

- **Streamlit**: Web application framework
- **LangChain**: LLM framework and chains
- **FAISS**: Vector similarity search
- **HuggingFace**: Embedding models
- **Pandas**: Data manipulation
- **PyDrive**: Google Drive API access (for technician agent)
- **Crawl4AI**: Web scraping (optional, for data collection)

## Data Collection

The project includes web scraping scripts to collect product data:

- **Hikvision Scraper**: `scripts/hikvision_scraper.py` - Scrapes Hikvision product data
- **Satel Scraper**: `scripts/satel_scraper.py` - Scrapes Satel product data

See `scripts/README.md` for detailed usage instructions.

## Important Files Location

### Credentials (Project Root Directory)
```
Rag_chatbot/
├── app.py
├── client_secrets.json      ← Place Google Drive credentials here
├── credentials.json         ← Created automatically (don't commit)
└── ...
```

Both files are already in `.gitignore` - they will NOT be committed to GitHub.

## Notes

- The application uses Groq API (via OpenAI-compatible interface) by default
- FAISS indices are cached in session state for performance
- Product indices are built on first run (may take time)
- The technician agent requires Google Drive API access (see `CREDENTIALS_SETUP.md`)
- Web scraping scripts require `crawl4ai` and `beautifulsoup4` (optional dependencies)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
