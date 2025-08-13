# 🌐 Web Content Preprocessor

---

>> **A modular, high-performance preprocessing pipeline for cleaning and structuring messy, repetitive, or unstructured web data into high-quality, categorized, deduplicated chunks ready for downstream analysis or machine learning.**


This package is designed for scalability, customization, and accuracy, making it ideal for data engineers, NLP practitioners, and AI developers working with large-scale web content.

---

## ✨ Key Features

- **🧹 Text Cleaning** – Remove noise patterns, unwanted metadata, and normalize formatting.

- **🌍 Language Detection** – Auto-detect and filter by supported languages.

- **🔍 Named Entity Recognition (NER)** – Extract entities such as organizations, people, locations, and products.

- **📂 Content Categorization** – Classify text into domains like Services, Industries, or Company profiles.

- **🏷️ Tag Extraction** – Generate relevant tags from both text and URLs.

- **🧠 Topic Extraction** – Derive key topics from titles, URLs, and text.

- **✂️ Intelligent Chunking** – Split text into overlapping, semantically coherent chunks.

- **♻️ Deduplication** – Remove identical or highly similar content via content hashing.

---

## 📂 Project Structure

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

---

## ⚙️ Installation

### Prerequisites

```bash
pip install nltk spacy langdetect

python -m spacy download en_core_web_sm

```

>> **Note: NLTK data (e.g., punkt) is automatically downloaded on first run.**

---

## 🚀 Usage

### Command Line Interface

```bash
# Process a single JSONL file
python run_preprocessor.py --input data/input.jsonl --output data/output.jsonl

# Process a directory of files
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

# Initialize
preprocessor = Preprocessor(verbose=True)

# Process single file
preprocessor.preprocess_jsonl_file("data/input.jsonl", "data/output.jsonl")

# Process multiple files in directory
preprocessor.preprocess_directory("data/input_dir", "data/output.jsonl")

# Process an individual record
record = {"content" : "Sample text", "url" : "https://example.com"}

chunks = preprocessor.process_record(record)

```

### Using Individual Components

```python
from preprocessor.core import TextCleaner, ChunkBuilder, NamedEntityRecognizer

# Clean text
cleaned_text = TextCleaner().clean_text(raw_text)

# Create chunks
chunks       = ChunkBuilder(max_tokens=512, overlap=50).chunk_text(cleaned_text)

# Extract entities
entities     = NamedEntityRecognizer().extract_named_entities(cleaned_text)
```

---

## ⚡ Configuration

Create a `config.py` file to customize default settings:

```python
MAX_TOKENS_PER_CHUNK = 512
CHUNK_OVERLAP        = 50
MIN_CHUNK_LENGTH     = 100
LANGUAGE             = "en"
SKIP_PHRASES         = ["example footer", "advertisement"]
```

---

## 📥 Input Format

The preprocessor expects JSONL files where each line is a JSON object with at least a `content` field:

```json
{"content": "Your web content here", "url": "https://example.com", "title": "Page Title"}
{"content": "More content...", "url": "https://another-example.com"}
```

---

## 📤 Output Format

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

---

## 🔍 Component Overview

| Component                 | Purpose                                       | Tech                  |
| ------------------------- | --------------------------------------------- | --------------------- |
| **TextCleaner**           | Removes noise, URLs, emails, unwanted symbols | Regex                 |
| **LanguageDetector**      | Identifies language, with fallback            | `langdetect`          |
| **NamedEntityRecognizer** | Extracts ORG, PERSON, GPE, PRODUCT            | `spaCy`               |
| **ContentCategorizer**    | Classifies by URL patterns & keywords         | Custom logic          |
| **TagExtractor**          | Generates topic/tech tags                     | Custom keyword maps   |
| **TopicExtractor**        | Multi-step topic generation                   | Title → URL → content |
| **ChunkBuilder**          | Creates overlapping, sentence-aware chunks    | Token length-based    |
| **Utils**                 | Hashing, text validation, stats               | Python stdlib         |

---

## 🛠 Advanced Customization

### Custom Skip Phrases

```python
custom_skip_phrases = ["custom footer text", "advertisement"]
preprocessor        = Preprocessor(skip_phrases=custom_skip_phrases)
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

---

## 📊 Performance Tips

- Use batch processing for large datasets.

- Limit NER to first 1000 chars for speed.

- Skip language detection for short texts.

- Deduplication hashes are stored in-memory.

---

## 📝 Logging

The package uses Python's built-in logging module. Set `verbose=True` for detailed processing information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
preprocessor = Preprocessor(verbose=True)
```

---

## 🛡 Error Handling

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

---

*This project showcases practical skills in web scraping, data processing, and software architecture. It demonstrates the ability to build production-ready tools with clean, maintainable code while considering ethical scraping practices and scalability challenges.*

