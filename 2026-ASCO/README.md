# ASCO 2026 Abstract Annotator

A web-based tool for searching, viewing, and annotating ASCO 2026 conference abstracts using OpenAI's language models. This tool provides an intuitive interface to browse, search, and analyze abstracts from the American Society of Clinical Oncology (ASCO) 2026 Annual Meeting.

## Features

- **Search & Filter**: Search abstracts by keywords (semicolon-separated) with matching keyword tracking
- **Abstract Viewing**:
  - Inline expansion with formatted section headers (Background, Methods, Results, Conclusions, Disclosures, Trial Registration, References)
  - Full-screen modal view with keyword highlighting
  - Direct links to the original abstracts on asco.org
- **AI-Powered Annotation**: Ask questions about abstracts and get AI-generated answers using OpenAI models
- **Parallel Processing**: Configurable multi-threaded processing for fast annotation of large datasets
- **Export Results**: Download filtered or annotated results as CSV files
- **Modern UI**: Clean, responsive interface with pagination and real-time progress tracking
- **Smart Sorting**: Abstracts are sorted by Abstract # (numeric IDs ascending first, then alphanumeric IDs like `LBA…` and `e…`)

## Prerequisites

- Python 3.7 or higher
- An OpenAI API key (for annotation features)
- Conference abstract data in Excel format (.xlsx)

## Installation

### Option 1: Using Conda (Recommended)

```bash
# Create a new conda environment
conda create -n conference-annotator python=3.9

# Activate the environment
conda activate conference-annotator

# Install required packages
pip install -r requirements.txt
```

### Option 2: Using pip with venv

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Option 3: System-wide installation

```bash
pip install -r requirements.txt
```

## Setup

1. **Prepare your data file**: This application is configured to use `asco_abstracts_full.xlsx` which should be placed in the same directory as `conference-webapp.py`.

2. **Excel file format**: The application expects the ASCO presentation export schema, which includes (among others):
   - `Abstract Number` — Abstract ID/number shown to users (e.g. `2503`, `LBA9001`, `e24207`)
   - `Title` — Abstract title
   - `Presenter` — Presenting author
   - `All Authors` — Full author list
   - `First Author`, `First Author Org` — First author and affiliation
   - `Session Title`, `Session Type`, `Session ID` — Session metadata
   - `Primary Track`, `Tracks` — Topic/track information
   - `Journal Citation`, `DOI` — Publication metadata
   - `Clinical Trial Registry Number`
   - `Body` — Full abstract text
   - `Link` — URL to the original presentation on asco.org

   On load, the application renames these to its internal schema and displays:
   - `Abstract ID` (← Abstract Number)
   - `Session Title`
   - `Title`
   - `Presenter`
   - `Authors` (← All Authors)
   - `Abstract` (← Body, with formatted section headers)
   - `Link` (← Link)

   **Note**: Abstracts are sorted by Abstract # in ascending order when loaded — numeric IDs first, then alphanumeric IDs (`LBA…`, `TPS…`, `e…`), then any rows without an abstract number.

3. **OpenAI API Key** (optional, required only for annotation):

   You can provide your OpenAI API key in two ways:

   **Method 1: Environment Variable (Recommended)**
   ```bash
   # Set the environment variable before running the app
   export OPENAI_API_KEY='sk-your-api-key-here'

   # Then run the application
   python conference-webapp.py
   ```

   **Method 2: Manual Entry**
   - Run the application without setting the environment variable
   - Enter your API key in the "Advanced Settings" section of the web interface
   - The key is stored in your browser session only

## Usage

### Starting the Application

**Basic Usage:**
```bash
conda activate conference-annotator
python conference-webapp.py

# If using venv
source venv/bin/activate  # On macOS/Linux
python conference-webapp.py
```

**Custom Host and Port:**
```bash
# Run on a different port
PORT=8080 python conference-webapp.py

# Bind to all interfaces (required for deployment)
HOST=0.0.0.0 PORT=8080 python conference-webapp.py

# With OpenAI API key
OPENAI_API_KEY='sk-your-key' HOST=0.0.0.0 PORT=8000 python conference-webapp.py
```

The application will start and display:
```
==================================================
ASCO 2026 Abstract Annotator
==================================================

Starting web server...
Open your browser and go to: http://127.0.0.1:5000

Press CTRL+C to stop the server
```

**Environment Variables:**
- `HOST` — Server host (default: `127.0.0.1`). Use `0.0.0.0` for deployment
- `PORT` — Server port (default: `5000`)
- `FLASK_DEBUG` — Enable debug mode (`True` or `False`, default: `False`)
- `OPENAI_API_KEY` — Your OpenAI API key (optional)

Open your browser and navigate to the displayed URL (default: `http://127.0.0.1:5000`)

### Production Deployment

For production environments, use **Gunicorn** instead of Flask's built-in development server. See [PRODUCTION.md](PRODUCTION.md) for detailed production deployment instructions.

**Quick production start:**
```bash
# Basic production server with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 conference-webapp:app

# With environment variables and timeout
OPENAI_API_KEY='sk-your-key' gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 conference-webapp:app
```

### Searching Abstracts

1. Enter keywords in the search box (separate multiple keywords with semicolons)
   - Example: `checkpoint inhibitor; melanoma; PD-1`
2. Click "Search" or press Enter
3. The table will update to show matching abstracts with highlighted keywords
4. Search works across all fields: Abstract #, Title, Authors, Session Title, Primary Track, Session Type, and Abstract text
5. Click "Reset Search" to view all abstracts

### Viewing Abstracts

- **Inline Expansion**: Click the blue `+` button to expand/collapse the abstract text
- **Modal View**: Click the purple `⊡` button to open the abstract in a full-screen modal with:
  - Formatted section headers (Background, Methods, Results, Conclusions, Trial Registration, References, Disclosures)
  - Keyword highlighting (if searched)
  - Abstract metadata (ID, Session, Presenter, Authors)
  - Direct link to the original abstract on asco.org
- **Original Abstract**: Click the "View" link in the Link column to open the original abstract on asco.org in a new tab

### Annotating Abstracts

1. Enter your question in the "Annotation Question" field
   - Example: "What immunotherapy combination is being studied?"
2. Click "▶ Advanced Settings" to configure:
   - **Model**: Select the OpenAI model
   - **API Key**: Enter your key or use environment variable
   - **Threads**: Number of parallel requests (capped at 20 for stability)
   - **Max Abstracts to Annotate**: Safety cap on how many abstracts a single run can process (default: 500)
   - **Results per page**: Pagination settings
   - **Dry Run**: Test without making API calls (uses mock responses)
   - **Show rows without abstract text**: Include/exclude empty abstracts
3. Click "Start Annotation"
4. Monitor progress in the progress bar
5. Once complete, the table will update with a new "Answer" column
6. Click "Download Results" to export as CSV

### Downloading Results

- **Current View**: Click "Download Results" to export the current filtered view as CSV
- **Annotated Results**: After annotation, download includes the answer column
- Files are named with timestamps for easy organization (e.g., `asco_abstracts_filtered_20260521_153000.csv`)

## Configuration

### Advanced Settings

- **Model Selection**: Choose from the OpenAI models exposed in the dropdown
- **Number of Threads**: Control parallel processing speed (1–20; capped at 20)
  - Higher values = faster processing but more API rate limit risk
- **Max Abstracts to Annotate**: Hard safety limit per annotation run (default 500)
- **Results per page**: 10, 20, 50, 100, or 200 abstracts per page
- **Dry Run Mode**: Test annotation workflow without API calls or costs

### Data Source

This application is specifically configured for ASCO 2026 abstracts:
- **Data file**: `asco_abstracts_full.xlsx`
- **Total presentations**: 7,730 (7,295 with abstract text)
- **Conference**: American Society of Clinical Oncology (ASCO) 2026 Annual Meeting
- **Original source**: https://meetings.asco.org/abstracts-presentations/search

Abstracts are sorted by Abstract # when loaded — numeric IDs ascending first, then alphanumeric IDs (e.g. `LBA…`, `TPS…`, `e…`), then any rows without an abstract number.

## API Costs

Annotation uses OpenAI's API and incurs costs based on:
- Number of abstracts
- Selected model
- Question complexity

**Tip**: Use "Dry Run" mode to test your workflow before running real annotations.

## Troubleshooting

### "Could not find asco_abstracts_full.xlsx"
- Ensure the `.xlsx` file is in the same directory as `conference-webapp.py`
- Check that the file name matches `asco_abstracts_full.xlsx`

### "Error code: 400" or API errors
- Verify your OpenAI API key is correct
- Check you have sufficient API credits
- Some models may not support all parameters — the app uses default settings for compatibility

### Port already in use
- Stop any other processes using port 5000
- Or run with a custom port: `PORT=8080 python conference-webapp.py`

### Data not loading properly
- Verify the Excel file matches the expected ASCO presentation export schema (see [Setup](#setup))
- Update the column-rename map in `load_data()` if your export uses different column names
- Ensure the Excel file is not corrupted

## Technical Details

- **Framework**: Flask web application with embedded HTML/CSS/JavaScript
- **Data Processing**: Pandas for Excel file handling and data manipulation
- **API Integration**: OpenAI SDK 2.x for language model access
- **Concurrency**: ThreadPoolExecutor for parallel API calls (capped at 20 workers)
- **Storage**: In-memory data processing, CSV exports via BytesIO

## License

See repository root [LICENSE](../LICENSE).

## Acknowledgments

Built for ASCO 2026 abstract analysis. Adapted from the AACR 2026 Abstract Annotator framework in this repository.
