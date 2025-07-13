# Investigation Processor

This tool processes ongoing trade investigations using either the Perplexity API or Google Gemini API to generate comprehensive market assessments and impact analyses.

## Features

- **Market Assessment**: Analyzes total market size, import volumes, and trade patterns
- **Tariff Impact Analysis**: Evaluates effects of 10%, 25%, and 50% tariffs
- **Company Impact Analysis**: Identifies affected companies with revenue and production data
- **Comprehensive Reporting**: Generates detailed JSON results and summary reports

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Get API Keys**:
   - **Perplexity API Key**: Visit [Perplexity AI Settings](https://www.perplexity.ai/settings/api)
   - **Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)

3. **Configure Environment**:
   ```bash
   # Create .env file
   cp env_example.txt .env
   
   # Edit .env and add your API keys
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Perplexity API Version
```bash
# Test with single investigation
python test_single_investigation.py

# Process all investigations
python investigation_processor.py
```

### Gemini API Version
```bash
# Test with single investigation
python test_single_investigation_gemini.py

# Process all investigations
python investigation_processor_gemini.py
```

## Output Files

The scripts generate several output files:

### Perplexity Version
1. **`investigation_results_YYYYMMDD_HHMMSS.json`**: Complete analysis results for all investigations
2. **`investigation_summary_report_YYYYMMDD_HHMMSS.md`**: Human-readable summary report
3. **`investigation_results_progress_N.json`**: Progress saves after each investigation

### Gemini Version
1. **`investigation_results_gemini_YYYYMMDD_HHMMSS.json`**: Complete analysis results for all investigations
2. **`investigation_summary_report_gemini_YYYYMMDD_HHMMSS.md`**: Human-readable summary report
3. **`investigation_results_gemini_progress_N.json`**: Progress saves after each investigation

## Analysis Structure

For each investigation, the tool provides:

### 1. Current Market Assessment
- Total market size (global and US)
- Import volumes and values
- Market share analysis
- Trade patterns and major exporters

### 2. Tariff Impact Analysis (10%, 25%, 50%)
- Cost estimates with unchanged trade patterns
- US companies' capacity to meet demand
- Domestic market shift estimates
- Supply chain and cost impacts
- Consumer price effects

### 3. Company Impact Analysis
- Major affected companies (US and foreign)
- Revenue and profit data
- Production geography
- Tariff impact estimates
- Strategic response options

### 4. Supply Chain Bottlenecks
- Critical small suppliers and downstream providers
- Sole-source or near-sole-source suppliers
- Overseas-only suppliers and tariff exceptions
- Market share opportunities for small companies
- Potential supply chain disruption points

### 5. Additional Considerations
- Retaliatory measures
- Related industry impacts
- Long-term implications
- Regulatory considerations

## Data Source

The tool processes investigations from `ongoing_investigations.json`, which includes:
- Section 232 investigations (national security)
- Section 301 investigations (unfair trade practices)
- Antidumping/Countervailing duty investigations

## Error Handling

- Automatic retries with exponential backoff
- Progress saving after each investigation
- Detailed error logging
- Graceful handling of API failures

## Rate Limiting

The scripts include delays between API calls to respect rate limits:
- **Perplexity**: 5-second delays between investigations
- **Gemini**: 5-second delays between investigations, 2-second delays between sections

## Shared Prompts

Both processors use shared prompt definitions in `prompts.py`, making it easy to:
- Maintain consistent analysis across both APIs
- Update prompts in one place
- Compare results between different AI models

## Customization

You can modify the analysis by editing the prompt functions in `prompts.py` to adjust the analysis scope or add additional questions. 