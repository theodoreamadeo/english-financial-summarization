# Indonesian Financial Summarization

Summarization for FinDDR2025 (Financial Document Deep Research Challenge 2025)

## Overview

This project provides automated summarization of Indonesian financial documents, specifically designed for the Financial Document Deep Research Challenge 2025. The system processes financial reports and generates structured markdown summaries.

## Project Structure

```
.
├── main.py                 # Main application entry point
├── output_sample.py        # Sample output generation utilities
├── output_structure.py     # Output structure management
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not tracked)
├── output/                # Generated output files
├── report_md/             # Source financial reports
```

## Features

- Automated financial document processing
- Structured markdown report generation
- Support for Indonesian financial documents
- Image processing and integration
- Configurable output formats

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd indonesian-financial-summarization
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

Run the main application:
```bash
python main.py
```

### Sample Output Generation
```bash
python output_sample.py
```

### Structure Management
```bash
python output_structure.py
```

## Input Format

The system processes financial reports in markdown format placed in the `report_md/` directory. Images should be stored in `report_md/images/`.

## Output

Generated summaries are saved in the `output/` directory as structured markdown files.

## Contributing

This project is part of the FinDDR2025 challenge. Please follow the challenge guidelines when contributing.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Challenge Information

**FinDDR2025 (Financial Document Deep Research Challenge 2025)**
- Focus: Indonesian financial document summarization
- Goal: Automated processing and summarization of financial reports
- Output: Structured, readable financial summaries

## Contact

For questions related to this FinDDR2025 submission, please refer to the challenge documentation.
