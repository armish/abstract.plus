# Conference Abstract Annotator

A web-based tool for searching, viewing, and annotating conference abstracts using OpenAI's language models. Originally developed for ESMO 2025, this tool can be adapted for any medical or scientific conference with abstract data in Excel format.

## Features

- **Search & Filter**: Search abstracts by keywords (semicolon-separated) with matching keyword tracking
- **Abstract Viewing**:
  - Inline expansion with formatted section headers (Background, Methods, Results, Conclusions, etc.)
  - Full-screen modal view with keyword highlighting
- **AI-Powered Annotation**: Ask questions about abstracts and get AI-generated answers using OpenAI models
- **Parallel Processing**: Configurable multi-threaded processing for fast annotation of large datasets
- **Export Results**: Download filtered or annotated results as CSV files
- **Modern UI**: Clean, responsive interface with pagination and real-time progress tracking

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

1. **Prepare your data file**: Place your Excel file containing abstract data in the same directory as `conference-webapp.py`. The application will automatically detect files with these names (in priority order):
   - `2025 ESMO - All combined - raw.xlsx`
   - `2025 ESMO Abstracts.xlsx`
   - `ESMO_Abstracts.xlsx`
   - `2025 ASCO - Abstracts.xlsx`
   - `2025 ASCO Abstracts.xlsx`
   - `ASCO_Abstracts.xlsx`
   - `abstracts.xlsx`
   - Or any other `.xlsx` file in the directory

2. **Excel file format**: Your Excel file should contain columns for:
   - Abstract ID/Number (e.g., "Poster ID" or "Abstract #")
   - Abstract Title (e.g., "Poster Title" or "Abstract title")
   - Author information (e.g., "Presenting Author" or "First Author")
   - Category/Track
   - Abstract text

   The application automatically maps common column names:
   - `Poster ID` → `Abstract #`
   - `Poster Title` → `Abstract title`
   - `Presenting Author` → `First Author`
   - `Category` → `Track`

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
# If using conda
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
ESMO 2025 Abstract Annotator
==================================================

Starting web server...
Open your browser and go to: http://127.0.0.1:5000

Press CTRL+C to stop the server
```

**Environment Variables:**
- `HOST` - Server host (default: `127.0.0.1`). Use `0.0.0.0` for deployment
- `PORT` - Server port (default: `5000`)
- `OPENAI_API_KEY` - Your OpenAI API key (optional)

Open your browser and navigate to the displayed URL (default: `http://127.0.0.1:5000`)

### Searching Abstracts

1. Enter keywords in the search box (separate multiple keywords with semicolons)
   - Example: `breast cancer; immunotherapy; PD-L1`
2. Click "Search" or press Enter
3. The table will update to show matching abstracts with highlighted keywords
4. Click "Reset Search" to view all abstracts

### Viewing Abstracts

- **Inline Expansion**: Click the blue `+` button to expand/collapse the abstract text
- **Modal View**: Click the purple `⊡` button to open the abstract in a full-screen modal with:
  - Formatted section headers (Background, Methods, Results, Conclusions)
  - Keyword highlighting (if searched)
  - Abstract metadata (ID, Author, Track)

### Annotating Abstracts

1. Enter your question in the "Annotation Question" field
   - Example: "Does this study involve combination therapy?"
2. Click "▶ Advanced Settings" to configure:
   - **Model**: Select the OpenAI model (default: GPT-5 Nano)
   - **API Key**: Enter your key or use environment variable
   - **Threads**: Number of parallel requests (default: 100)
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
- Files are named with timestamps for easy organization

## Configuration

### Advanced Settings

- **Model Selection**: Choose from GPT-5 (nano/mini/full), GPT-4o, or GPT-4 series
- **Number of Threads**: Control parallel processing speed (1-200)
  - Higher values = faster processing but more API rate limit risk
  - Recommended: 50-100 for most use cases
- **Results per page**: 10, 20, 50, 100, or 200 abstracts per page
- **Dry Run Mode**: Test annotation workflow without API calls or costs

### Customizing for Different Conferences

To adapt this tool for a different conference:

1. Update the Excel file name in `conference-webapp.py` line 1239-1247
2. Modify the column mapping in lines 1271-1276 if needed
3. Update the header title and link in the HTML template (lines 535-539)

## API Costs

Annotation uses OpenAI's API and incurs costs based on:
- Number of abstracts
- Selected model
- Question complexity

Approximate costs (as of 2025):
- GPT-5 Nano: Most cost-effective
- GPT-5 Mini: Balanced cost/performance
- GPT-5: Highest quality, higher cost
- GPT-4o-mini: Good middle ground

**Tip**: Use "Dry Run" mode to test your workflow before running real annotations.

## Troubleshooting

### "No Excel file found"
- Ensure your `.xlsx` file is in the same directory as `conference-webapp.py`
- Check that the file name matches one of the expected names or is the only `.xlsx` file

### "Error code: 400" or API errors
- Verify your OpenAI API key is correct
- Check you have sufficient API credits
- Some models may not support all parameters - the app uses default settings for compatibility

### Port already in use
- Stop any other processes using port 5000
- Or run with a custom port: `PORT=8080 python conference-webapp.py`

### Data not loading properly
- Verify Excel file format matches expected columns
- Check for column name variations and update mapping in code if needed
- Ensure Excel file is not corrupted

## Technical Details

- **Framework**: Flask web application with embedded HTML/CSS/JavaScript
- **Data Processing**: Pandas for Excel file handling and data manipulation
- **API Integration**: OpenAI SDK 2.x for language model access
- **Concurrency**: ThreadPoolExecutor for parallel API calls
- **Storage**: In-memory data processing, CSV exports via BytesIO

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

For issues, questions, or feature requests, please [open an issue on GitHub/contact information].

## Acknowledgments

Originally developed for ESMO 2025 conference abstract analysis. Adapted from ASCO 2025 Abstract Annotator.
