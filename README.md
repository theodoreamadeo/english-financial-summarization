# English Financial Summarization

Automated comparative analysis of company annual reports using AI-powered document processing and financial analysis.

## Overview

This project automates the process of analyzing and comparing company annual reports across multiple fiscal years. It converts PDF annual reports to markdown format, then uses AI language models to generate comprehensive comparative financial analysis reports following a structured format.

**Key Capabilities:**
- Converts PDF annual reports to structured markdown using MinerU API
- Generates in-depth comparative analysis for fiscal years 2023 and 2024
- Processes multiple companies in batch mode automatically
- Produces standardized financial analysis reports with detailed sections
- Supports various AI models (Google Gemini, OpenAI, etc.) via OpenRouter

## Features

- **Automated PDF to Markdown Conversion**: Uses MinerU API with OCR, formula, and table extraction
- **Batch Processing**: Process multiple companies automatically without manual intervention
- **Structured Analysis**: Generates reports following predefined output structure and regulations
- **Token Usage Tracking**: Monitors and logs token consumption for cost management
- **Error Handling**: Robust retry mechanisms and error tracking for failed companies
- **Progress Tracking**: Real-time progress updates and comprehensive batch summaries
- **Flexible Model Support**: Works with multiple AI models through OpenRouter API

## Project Structure

```
.
├── main.py                      # Main application with batch processing logic
├── output_sample.py             # Sample output format examples
├── output_structure.py          # Report structure definitions
├── output_regulation.py         # Analysis guidelines and requirements
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (API keys)
├── data/                        # Input data and samples
│   └── sample/                  # Sample documents
├── report_md/                   # Converted markdown reports (auto-generated)
│   ├── CompanyName_2023.md
│   └── CompanyName_2024.md
├── output/                      # Generated analysis reports
│   └── CompanyName_report.md
├── evaluation/                  # Evaluation tools and results
│   ├── report_evaluator.py
│   └── result/
└── result/                      # Additional results and outputs
```

## Installation

### Prerequisites
- Python 3.8 or higher
- API keys for MinerU and OpenRouter

### Setup Steps

1. **Clone the repository:**
```bash
git clone <repository-url>
cd english-financial-summarization
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**

Create a `.env` file in the project root:
```env
MINERU_API_KEY=your_mineru_api_key_here
OPEN_ROUTER_API_KEY=your_openrouter_api_key_here
```

To obtain API keys:
- **MinerU API**: Sign up at [https://mineru.net](https://mineru.net)
- **OpenRouter API**: Sign up at [https://openrouter.ai](https://openrouter.ai)

## Usage

### Basic Usage

1. **Configure companies to process** in `main.py`:

```python
COMPANIES = [
    {
        "name": "Company Name",
        "enabled": True,  # Set to True to process, False to skip
        "files": [
            ("Company_Name_2024.pdf", "https://url-to-2024-report.pdf"),
            ("Company_Name_2023.pdf", "https://url-to-2023-report.pdf"),
        ]
    },
    # Add more companies...
]
```

2. **Run the batch processor:**
```bash
python main.py
```

The script will:
- Download and convert PDFs to markdown (if not already converted)
- Process each enabled company sequentially
- Generate comparative analysis reports
- Save reports to the `output/` directory
- Display a summary of successful and failed processes

### Processing Flow

```
1. PDF Download → 2. PDF to Markdown Conversion → 3. AI Analysis → 4. Report Generation
```

For each company:
- **Step 1**: Downloads PDF files from provided URLs
- **Step 2**: Converts PDFs to markdown using MinerU API
- **Step 3**: Analyzes reports using AI model (section by section)
- **Step 4**: Saves comprehensive comparative report

### Output Format

Generated reports include:
- Executive Summary
- Financial Performance Analysis
- Balance Sheet Analysis
- Cash Flow Analysis
- Key Financial Ratios
- Risk Assessment
- Strategic Initiatives
- Year-over-Year Comparisons
- And more detailed sections...

## Configuration

### Selecting AI Model

Change the model in `main.py`:
```python
# Google Gemini (default)
model = Model("google", "gemini-2.5-flash")

# OpenAI
model = Model("openai", "o1-preview")
```

### Adjusting Processing Delays

Modify delays in `main.py`:
```python
delay_seconds = 65  # Between sections (default: 65s)
delay_seconds = 120  # Between companies (default: 120s)
```

### Customizing Analysis Structure

Edit these files to customize report format:
- `output_structure.py`: Define report sections and subsections
- `output_regulation.py`: Specify analysis requirements and questions
- `output_sample.py`: Provide format examples

## Batch Processing

The batch processing system allows you to:

1. **Enable/disable companies** individually using the `"enabled"` flag
2. **Track progress** with detailed logging
3. **View summaries** showing successful and failed companies
4. **Resume processing** - already converted PDFs are skipped

### Batch Output Example:
```
================================================================================
BATCH PROCESSING STARTED
Total companies to process: 5
================================================================================

[BATCH] Processing company 1/5: Rolls-Royce Holdings PLC
...
[SUCCESS] Rolls-Royce_Holdings_PLC_report.md saved

[BATCH] Processing company 2/5: Gamma Communications PLC
...

================================================================================
BATCH PROCESSING COMPLETED
================================================================================
Successful: 4/5
  ✓ Rolls-Royce Holdings PLC
  ✓ Gamma Communications PLC
  ✓ Babcock International Group PLC
  ✓ QinetiQ Group PLC

Failed: 1/5
  ✗ Select Harvests
================================================================================
```

## Token Usage Monitoring

The system automatically tracks and logs token usage:
- Combined PDF text tokens
- Per-section prompt tokens
- Helps estimate API costs
- Useful for debugging large documents

## Troubleshooting

### Common Issues

**PDF Conversion Fails:**
- Check MinerU API key is valid
- Verify PDF URL is accessible
- Check API rate limits

**AI Analysis Errors:**
- Verify OpenRouter API key
- Check model availability
- Monitor token limits
- Ensure sufficient API credits

**Missing Output:**
- Check `output/` directory permissions
- Verify report generation completed all sections
- Look for error messages in console output

### Debug Mode

Enable verbose logging by checking console output during execution.

## Example Companies

The project includes configurations for various companies across different sectors:
- Technology (NVIDIA, NEXTDC, Spark New Zealand)
- Healthcare (UnitedHealth, Centene)
- Retail (The Home Depot, DICK'S Sporting Goods, Metcash)
- Defense (Babcock, QinetiQ, Rolls-Royce)
- And more...

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **MinerU API** for PDF to Markdown conversion
- **OpenRouter** for unified AI model access
- **Google Gemini** for powerful language model capabilities

## Support

For questions or issues:
- Open an issue on GitHub
- Check existing documentation
- Review error logs for debugging

---

**Note**: This tool is designed for financial analysis purposes. Always verify AI-generated analysis with official financial documents and professional financial advice.
