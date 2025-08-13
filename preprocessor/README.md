# Web Content Preprocessor

A modular preprocessing pipeline for handling messy, repetitive web data and converting it into structured chunks for further processing. This package is designed to clean, deduplicate, categorize, and chunk web content efficiently.

## Features

- **Text Cleaning**: Remove noise patterns, URLs, emails, and normalize formatting
- **Language Detection**: Automatically detect and filter content by language
- **Named Entity Recognition**: Extract organizations, persons, locations, and products
- **Content Categorization**: Automatically categorize content (Services, Industries, Company, etc.)
- **Topic Extraction**: Extract meaningful topics from titles, URLs, and content
- **Intelligent Chunking**: Split content into overlapping chunks with validation
- **Deduplication**: Remove duplicate content using content hashing
- **Tag Extraction**: Extract relevant tags from content and URL patterns

## Project Structure

```
preprocessor/
├── __init__.py                          # Package initialization
├── core/                                # Core preprocessing modules
│   ├── __init__.py
│   ├── chunk_builder.py                 # Text chunking with overlap
│   ├── content_categorizer.py           # Content categorization
│   ├── language_detector.py             # Language detection
│   ├── named_entity_recognition.py      # NER using spaCy
│   ├── tag_extractor.py                 # Tag extraction from content/URLs
│   ├── text_cleaner.py                  # Text cleaning and noise removal
│   ├── topic_extractor.py               # Topic extraction
│   └── utils.py                         # Utility functions and validation
└── run_preprocessor.py                  # Main execution script
```

## Installation

### Prerequisites

```bash
pip install nltk spacy langdetect
python -m spacy download en_core_web_sm
```

### NLTK Data

The package will automatically download required NLTK data (punkt tokenizer) on first use.

## Usage

### Command Line Interface

```bash
# Process a single JSONL file
python run_preprocessor.py --input data/input.jsonl --output data/output.jsonl

# Process all files in a directory
python run_preprocessor.py --input data/input_dir --output data/output.jsonl --directory

# With custom parameters
python run_preprocessor.py \
    --input data/input.jsonl \
    --output data/output.jsonl \
    --max-tokens 1024 \
    --overlap 100 \
    --min-length 150 \
    --language en \
    --verbose
```

### Programmatic Usage

```python
from preprocessor import Preprocessor

# Initialize with default settings
preprocessor = Preprocessor(verbose=True)

# Process a single JSONL file
chunk_count = preprocessor.preprocess_jsonl_file(
    input_file="data/input.jsonl",
    output_file="data/output.jsonl"
)

# Process a directory of files
chunk_count = preprocessor.preprocess_directory(
    input_dir="data/input_directory",
    output_path="data/combined_output.jsonl"
)

# Process individual records
record = {"content": "Your text content here", "url": "https://example.com"}
chunks = preprocessor.process_record(record)
```

### Using Individual Components

```python
from preprocessor.core import TextCleaner, ChunkBuilder, NamedEntityRecognizer

# Text cleaning
cleaner = TextCleaner()
cleaned_text = cleaner.clean_text(raw_text)

# Chunking
chunk_builder = ChunkBuilder(max_tokens=512, overlap=50)
chunks = chunk_builder.chunk_text(cleaned_text)

# Named entity recognition
ner = NamedEntityRecognizer()
entities = ner.extract_named_entities(text)
```

## Configuration

Create a `config.py` file to customize default settings:

```python
# config.py
MAX_TOKENS_PER_CHUNK = 512
CHUNK_OVERLAP = 50
MIN_CHUNK_LENGTH = 100
LANGUAGE = "en"
SKIP_PHRASES = ["custom phrase to skip"]
```

## Input Format

The preprocessor expects JSONL files where each line is a JSON object with at least a `content` field:

```json
{"content": "Your web content here", "url": "https://example.com", "title": "Page Title"}
{"content": "More content...", "url": "https://another-example.com"}
```

## Output Format

The preprocessor generates JSONL files with structured chunks:

```json
{
  "content": "Processed chunk content...",
  "chunk_id": 0,
  "source": "https://example.com",
  "title": "Page Title",
  "entities": ["Organization Name", "Person Name"],
  "tags": ["Web Development", "Technology"],
  "category": "Services",
  "topic": "Web Development Services",
  "language": "en"
}
```

## Component Details

### TextCleaner
- Removes web noise patterns (multiple newlines, spaces, pipe separators)
- Filters out URLs, email addresses, and copyright notices
- Normalizes punctuation and whitespace

### LanguageDetector
- Uses `langdetect` library for language identification
- Handles short text gracefully
- Configurable default language fallback

### NamedEntityRecognizer
- Uses spaCy's `en_core_web_sm` model
- Extracts ORG, PERSON, GPE, and PRODUCT entities
- Filters out common web noise entities

### ContentCategorizer
- URL-based categorization using path patterns
- Content-based categorization using keyword matching
- Supports custom category definitions

### TagExtractor
- Extracts technology and business-related tags
- Processes both URL paths and content
- Supports custom keyword mappings

### TopicExtractor
- Multi-strategy topic extraction (title → URL → content)
- Intelligent sentence selection for content-based topics
- URL path component processing

### ChunkBuilder
- Sentence-aware chunking with configurable overlap
- Content validation and deduplication
- Comprehensive chunk quality filtering

### Utils
- Content hashing for deduplication
- Text quality validation
- Processing statistics

## Advanced Usage

### Custom Skip Phrases

```python
custom_skip_phrases = ["custom footer text", "advertisement"]
preprocessor = Preprocessor(skip_phrases=custom_skip_phrases)
```

### Custom Categories and Tags

```python
# Add custom categorization patterns
preprocessor.content_categorizer.add_url_patterns("Custom", ["/custom/"])
preprocessor.content_categorizer.add_content_keywords("Custom", ["keyword"])

# Add custom tag mappings
preprocessor.tag_extractor.add_custom_keywords({"ai": ["Artificial Intelligence"]})
```

### Batch Processing with Statistics

```python
preprocessor = Preprocessor(verbose=True)

# Process multiple files
files = ["file1.jsonl", "file2.jsonl", "file3.jsonl"]
total_chunks = 0

for file in files:
    chunks = preprocessor.preprocess_jsonl_file(file, f"output_{file}")
    total_chunks += chunks

# Get processing statistics
stats = preprocessor.get_processing_stats()
print(f"Total chunks: {total_chunks}")
print(f"Unique content pieces: {stats['utils']['unique_content_hashes']}")
```

## Performance Considerations

- **Memory Usage**: The deduplication system stores content hashes in memory
- **Processing Speed**: NER is limited to first 1000 characters for efficiency
- **Batch Size**: Process large files in chunks if memory is constrained
- **Language Detection**: Skipped for very short texts to improve performance

## Logging

The package uses Python's built-in logging module. Set `verbose=True` for detailed processing information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
preprocessor = Preprocessor(verbose=True)
```

## Error Handling

The preprocessor includes comprehensive error handling:
- Invalid JSON records are skipped with logging
- Failed language detection falls back to default language
- NER failures are logged but don't stop processing
- File I/O errors are handled gracefully

## Dependencies

- `nltk`: Text tokenization
- `spacy`: Named entity recognition
- `langdetect`: Language detection
- `re`: Regular expressions for text cleaning
- `hashlib`: Content hashing for deduplication
- `json`: JSON processing
- `logging`: Comprehensive logging
