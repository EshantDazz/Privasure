# SAR Redactions App

## Overview
The SAR Redactions App is a Streamlit-based application designed to process PDF documents and identify sensitive information for redaction. It uses advanced NLP techniques and AI models to detect and redact Personal Identifiable Information (PII), pronouns, and contextual information while preserving references to a specified subject.

## Features
- PDF document processing and text extraction
- Identification of PII entities using Azure services
- Detection and analysis of pronouns and parts of speech
- Subject-aware redaction that preserves subject-related information
- Alias identification for the main subject
- Generation of comprehensive Excel reports with detailed redaction analysis
- Real-time cost tracking for AI model usage
- Interactive web interface using Streamlit

## Prerequisites
- Python 3.8+
- Azure OpenAI API access
- Azure PII detection service access
- Spacy's English language model

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Install Spacy's English language model:
```bash
python -m spacy download en_core_web_sm
```

4. If you encounter numpy conflicts, run:
```bash
pip install --no-deps --force-reinstall numpy==1.26.4
```

## Environment Setup

Create a `.env` file in the project root with the following variables:
```
AZURE_PII_KEY=your_pii_key
AZURE_PII_ENDPOINT=your_pii_endpoint
AZURE_OPENAI_API_VERSION=your_api_version
AZURE_OPENAI_CHAT_MODEL_ADVANCE=your_model_name
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Access the web interface at `http://localhost:8501`

3. Enter the subject name (the person whose information should be preserved)

4. Upload PDF files for processing

5. Click "Process PDFs" to start the analysis

## Processing Pipeline

1. **Document Processing**
   - PDF text extraction
   - Initial PII detection
   - Parts of speech analysis

2. **Context Analysis**
   - Entity context extraction
   - Pronoun context analysis
   - Subject alias identification

3. **Redaction Generation**
   - Entity-based redaction
   - Pronoun-based redaction
   - Context-aware filtering

4. **Report Generation**
   - Comprehensive Excel report
   - Summary statistics
   - Detailed redaction analysis
   - Pronoun analysis

## Output Format

The application generates an Excel report containing:
- Summary statistics
- Entity detection results
- Redaction analysis
- Pronoun redaction details
- Source context information

## Notes

- The application uses multiple AI models for different aspects of analysis
- Processing time depends on document size and complexity
- Cost tracking is provided for AI model usage
- All redactions preserve subject-related information

## Troubleshooting

If you encounter any issues:

1. **Numpy Conflicts**
   ```bash
   pip install --no-deps --force-reinstall numpy==1.26.4
   ```

2. **Missing Spacy Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Environment Variables**
   - Ensure all required environment variables are properly set in `.env`
   - Check Azure API access and credentials

