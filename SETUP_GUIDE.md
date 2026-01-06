# NLWeb-MAIDAP Setup Guide

This guide documents the steps to set up and run the NLWeb multi-site podcast search system.

## Prerequisites

- Python 3.13
- Azure OpenAI account with text-embedding-3-large model deployment
- Git configured with Windows Credential Manager
- All configuration files already set up (via git)

## Initial Setup

### 1. Install Required Packages

The system requires `certifi` for SSL certificate verification on Windows:

```powershell
pip install certifi
```

### 2. Configure Python Environment

From the `code/python` directory:

```powershell
cd code/python
python -m venv myenv
.\myenv\Scripts\Activate.ps1
pip install -r ../../requirements.txt
```

## Loading Podcast Data

### Step 1: Load Podcast RSS Feeds

Load RSS feeds into individual site collections. The site name becomes the collection identifier:

```powershell
# Behind the Tech podcast (374 episodes)
python -m data_loading.db_load https://feeds.libsyn.com/121695/rss Behind-the-Tech --database qdrant_local

# Wait Wait Don't Tell Me from NPR (example - replace with actual RSS URL)
python -m data_loading.db_load https://www.npr.org/rss/podcast.php?id=344098539 Wait_Wait_NPR --database qdrant_local
```

### Step 2: Create Site Metadata File

Create `../../data/podcast_sites.json` (from the `code/python` directory) with site descriptions in JSONL format (one JSON object per line):

```json
{"name": "Behind the Tech with Kevin Scott", "site": "nlweb_sites", "url": "Behind-the-Tech", "text": "Behind the Tech podcast featuring Kevin Scott, CTO of Microsoft. Interviews with technology leaders, innovators, and pioneers covering topics like artificial intelligence, software development, machine learning, entrepreneurship, and tech culture. Episodes include conversations with industry leaders about their career journeys and technical innovations.", "schema_json": "{\"@type\": \"Podcast\", \"name\": \"Behind the Tech\", \"host\": \"Kevin Scott\", \"topics\": [\"AI\", \"software development\", \"technology\", \"innovation\", \"entrepreneurship\"], \"description\": \"Podcast about technology leaders and innovation\"}"}
{"name": "Wait Wait Don't Tell Me from NPR", "site": "nlweb_sites", "url": "Wait_Wait_NPR", "text": "Wait Wait Don't Tell Me is NPR's weekly news quiz show. Hosted by Peter Sagal, the show tests panelists and contestants on current events, politics, sports, science, and culture with humor and wit. Features celebrity guests, listener games, and comedy commentary on the week's news.", "schema_json": "{\"@type\": \"Podcast\", \"name\": \"Wait Wait Don't Tell Me\", \"host\": \"Peter Sagal\", \"topics\": [\"news\", \"current events\", \"comedy\", \"politics\", \"culture\"], \"description\": \"NPR's weekly news quiz show\"}"}
```

**Critical**: The `url` field must exactly match the site name used when loading episodes (e.g., "Behind-the-Tech" must match exactly).

### Step 3: Load Site Metadata and Generate Embeddings

This command reads the JSON file, generates embeddings via Azure OpenAI, and stores them in the `nlweb_sites` collection:

```powershell
python -m data_loading.db_load ../../data/podcast_sites.json nlweb_sites
```

The system automatically:
- Calls Azure OpenAI embedding API (maidap-text-embedding-3-large)
- Generates 3072-dimensional vectors from the `text` field
- Stores embeddings in Qdrant database
- Caches embeddings to `code/data/json_with_embeddings/podcast_sites.json`

## Verify Database Contents

```powershell
python check_qdrant_data.py
```

Expected output:
- Shows total document count (e.g., 376 = 374 episodes + 2 metadata entries)
- Lists collections: `nlweb_sites`, `Behind-the-Tech`, `Wait_Wait_NPR`
- Sample documents from each collection

## Architecture Overview

### Two-Layer System

1. **Metadata Layer** (`nlweb_sites` collection)
   - Contains site descriptions and metadata
   - Used by WHO endpoint to find relevant sites
   - 1 document per podcast site

2. **Content Layer** (individual site collections)
   - Contains actual podcast episodes
   - Queried after WHO discovers relevant sites
   - Many documents per podcast site

### Query Flow

1. User queries with `site=all`
2. WHO handler searches `nlweb_sites` collection for relevant sites
3. Multi-site handler queries each discovered site collection
4. Results are aggregated and returned

## Running the Server

```powershell
cd code/python
python -m aiohttp.web -H localhost -P 8000 webserver:app
```

Server runs on http://localhost:8000

## Testing Queries

### Test WHO Endpoint
```powershell
curl "http://localhost:8000/api/who?query=podcast+episodes"
```

Expected: Returns list of relevant sites

### Test Multi-Site Query
```powershell
curl "http://localhost:8000/api/query?query=technology+interviews&site=all&num_results=20"
```

Expected: Returns combined results from multiple sites

### Test Individual Site Query
```powershell
curl "http://localhost:8000/api/query?query=artificial+intelligence&site=Behind-the-Tech&num_results=10"
```

Expected: Returns results from specific site only

## Adding New Podcasts

1. Load the RSS feed:
   ```powershell
   python -m data_loading.db_load https://example.com/feed.rss NewPodcastName --database qdrant_local
   ```

2. Add metadata entry to `../../data/podcast_sites.json`:
   ```json
   {"name": "New Podcast Title", "site": "nlweb_sites", "url": "NewPodcastName", "text": "Description of the podcast covering topics and themes...", "schema_json": "{\"@type\": \"Podcast\", \"name\": \"...\"}"}
   ```

3. Reload metadata:
   ```powershell
   python -m data_loading.db_load ../../data/podcast_sites.json nlweb_sites
   ```

4. Restart the server

## Configuration Notes

The following files are already configured in the repository:

- `code/python/data_loading/db_load.py` - SSL certificate handling with certifi
- `config/config_embedding.yaml` - Azure OpenAI with maidap-text-embedding-3-large (3072 dims)
- `config/config_retrieval.yaml` - Only qdrant_local enabled
- `code/python/core/whoHandler.py` - Queries nlweb_sites collection for site discovery

## Common Issues

### SSL Certificate Errors
**Error**: `unable to get local issuer certificate`

**Fix**: Ensure `certifi` is installed: `pip install certifi`

### Site Name Mismatch
**Error**: Individual site queries fail

**Fix**: Verify the `url` field in metadata exactly matches the site name used when loading episodes

### No Embeddings Generated
**Issue**: Embeddings aren't created automatically

**Fix**: The `db_load.py` script automatically generates embeddings when loading JSON files. No manual embedding generation is needed.

## Database Location

Qdrant database files: `data/db/` (gitignored)

## Environment Variables

Ensure you have set:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- Other keys in `code/set_keys.sh` (not tracked in git)
