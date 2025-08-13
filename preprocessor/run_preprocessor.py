# Dependencies
import os
import json
import logging
import argparse
from typing import Dict
from typing import List
from core.utils import Utils
from core.text_cleaner import TextCleaner
from core.tag_extractor import TagExtractor
from core.chunk_builder import ChunkBuilder
from core.topic_extractor import TopicExtractor
from core.language_detector import LanguageDetector
from core.content_categorizer import ContentCategorizer
from core.named_entity_recognition import NamedEntityRecognizer


# Import config if available
try:
    import config
    MAX_TOKENS_PER_CHUNK = getattr(config, 'MAX_TOKENS_PER_CHUNK', 512)
    CHUNK_OVERLAP        = getattr(config, 'CHUNK_OVERLAP', 50)
    MIN_CHUNK_LENGTH     = getattr(config, 'MIN_CHUNK_LENGTH', 100)
    SKIP_PHRASES         = getattr(config, 'SKIP_PHRASES', [])
    LANGUAGE             = getattr(config, 'LANGUAGE', 'en')

except ImportError:
    # Default values if config not available
    MAX_TOKENS_PER_CHUNK = 512
    CHUNK_OVERLAP        = 50
    MIN_CHUNK_LENGTH     = 100
    SKIP_PHRASES         = []
    LANGUAGE             = 'en'


class Preprocessor:
    """
    Main preprocessor class that orchestrates all preprocessing components
    """
    def __init__(self, max_tokens: int = MAX_TOKENS_PER_CHUNK, overlap: int = CHUNK_OVERLAP, min_chunk_len: int = MIN_CHUNK_LENGTH,
                 skip_phrases: List[str] = SKIP_PHRASES, language: str = LANGUAGE, verbose: bool = False):
        """
        Initialize Enhanced Preprocessor with all components
        
        Arguments:
        -----------
            max_tokens     { int } : Maximum tokens per chunk

            overlap        { int } : Number of tokens to overlap between chunks
            
            min_chunk_len  { int } : Minimum chunk length

            skip_phrases  { list } : List of phrases to skip

            language       { str } : Target language for processing

            verbose       { bool } : Enable verbose logging
        """
        self.max_tokens          = max_tokens
        self.overlap             = overlap
        self.min_chunk_len       = min_chunk_len
        self.language            = language
        self.verbose             = verbose
        
        # Initialize all components
        self.text_cleaner        = TextCleaner(skip_phrases = skip_phrases, 
                                               verbose      = verbose,
                                              )

        self.language_detector   = LanguageDetector(default_language = language, 
                                                    verbose          = verbose,
                                                   )

        self.ner                 = NamedEntityRecognizer(verbose = verbose)

        self.tag_extractor       = TagExtractor(verbose = verbose)

        self.content_categorizer = ContentCategorizer(verbose = verbose)

        self.topic_extractor     = TopicExtractor(verbose = verbose)

        self.chunk_builder       = ChunkBuilder(max_tokens       = max_tokens,
                                                overlap          = overlap,
                                                min_chunk_length = min_chunk_len,
                                                skip_phrases     = skip_phrases,
                                                verbose          = verbose,
                                               )

        self.utils               = Utils(verbose = verbose)
        
        # Setup logging
        logging.basicConfig(level = logging.DEBUG if verbose else logging.INFO)

        self.logger              = logging.getLogger("Preprocessor")

    
    def process_record(self, record: Dict, chunk_key: str = "content") -> List[Dict]:
        """
        Process a single record and return structured chunks
        
        Arguments:
        ----------
            record   { dict } : Input record dictionary

            chunk_key { str } : Key containing the content to process
            
        Returns:
        --------
             { list }         : List of processed chunk dictionaries
        """
        content    = record.get(chunk_key, "")
        url        = record.get("url", "")
        page_title = record.get("page_title", record.get("title", ""))
        
        if (not content or len(content.strip()) < 20):
            self.logger.debug(f"Skipping short content from {url}")
            return []
        
        # Language detection
        language = self.language_detector.detect_language(content)
        
        if (language != self.language):
            self.logger.debug(f"Skipping content due to language mismatch: {language}")
            return []
        
        # Clean content
        content_cleaned = self.text_cleaner.clean_text(content)
        
        if not content_cleaned:
            return []
        
        # Extract metadata
        entities         = self.ner.extract_named_entities(text = content_cleaned)

        tags             = self.tag_extractor.extract_tags_from_content_and_url(text = content_cleaned,
                                                                                url  = url,
                                                                               )

        category         = self.content_categorizer.categorize_content(text = content_cleaned, 
                                                                       url  = url,
                                                                      )

        topic            = self.topic_extractor.extract_topic(text  = content_cleaned, 
                                                              title = page_title, 
                                                              url   = url,
                                                             )
        
        # Create chunks
        chunks           = self.chunk_builder.chunk_text(text = content_cleaned)
        processed_chunks = list()
        
        for idx, chunk in enumerate(chunks):
            processed_chunks.append({"content"  : chunk,
                                     "chunk_id" : idx,
                                     "source"   : url,
                                     "title"    : page_title,
                                     "entities" : entities,
                                     "tags"     : tags,
                                     "category" : category,
                                     "topic"    : topic,
                                     "language" : language,
                                   })
        
        return processed_chunks

    
    def preprocess_jsonl_file(self, input_file: str, output_file: str) -> int:
        """
        Process JSONL file and output preprocessed chunks
        
        Arguments:
        ----------
            input_file  { str } : Path to input JSONL file

            output_file { str } : Path to output JSONL file
            
        Returns:
        --------
                { int }         : Number of chunks generated
        """
        all_chunks = list()
        self.logger.info(f"Starting preprocessing of {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        record = json.loads(line.strip())
                        chunks = self.process_record(record)
                        all_chunks.extend(chunks)
                        
                        if (line_num % 100 == 0):
                            self.logger.info(f"Processed {line_num} records, generated {len(all_chunks)} chunks")
                    
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON decode error at line {line_num}: {e}")
                    
                    except Exception as e:
                        self.logger.error(f"Error processing line {line_num}: {e}")
        
        except FileNotFoundError:
            self.logger.error(f"Input file not found: {input_file}")
            return 0
        
        except Exception as e:
            self.logger.error(f"Error reading input file: {e}")
            return 0
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok = True)
        
        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii = False) + '\n')
        
        self.logger.info(f"Preprocessing complete. {len(all_chunks)} chunks saved to {output_file}")
        
        return len(all_chunks)
    

    def preprocess_directory(self, input_dir: str, output_path: str) -> int:
        """
        Process all JSON/JSONL files in a directory
        
        Arguments:
        ----------
            input_dir   { str } : Directory containing input files

            output_path { str } : Path for output file
            
        Returns:
        --------
                  { int }       : Number of chunks generated
        """
        all_chunks = list()

        self.logger.info(f"Starting preprocessing of files in {input_dir}")
        
        for filename in os.listdir(input_dir):
            if filename.endswith(('.json', '.jsonl')):
                file_path = os.path.join(input_dir, filename)
                self.logger.info(f"Processing file: {file_path}")
                
                try:
                    with open(file_path, "r", encoding = "utf-8") as f:
                        if filename.endswith('.jsonl'):
                            
                            # Process JSONL line by line
                            for line in f:
                                try:
                                    record = json.loads(line.strip())
                                    all_chunks.extend(self.process_record(record))
                                
                                except json.JSONDecodeError as e:
                                    self.logger.error(f"JSON decode error in {filename}: {e}")
                        
                        else:
                            # Process single JSON object
                            try:
                                data = json.load(f)
                                
                                if isinstance(data, list):
                                    for record in data:
                                        all_chunks.extend(self.process_record(record))
                                
                                else:
                                    all_chunks.extend(self.process_record(data))
                            
                            except json.JSONDecodeError as e:
                                self.logger.error(f"JSON decode error in {filename}: {e}")
                
                except FileNotFoundError:
                    self.logger.error(f"File not found: {file_path}")
                
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok = True)
        
        # Write output
        with open(output_path, "w", encoding="utf-8") as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        
        self.logger.info(f"Preprocessing complete. {len(all_chunks)} chunks saved to {output_path}")
        
        return len(all_chunks)
    

    def get_processing_stats(self) -> Dict:
        """
        Get comprehensive processing statistics
        
        Returns:
        --------
            { dict }    : Dictionary with processing statistics
        """
        processing_stats =  {"chunk_builder" : self.chunk_builder.utils.get_stats(),
                             "utils"         : self.utils.get_stats(),
                            }

        return processing_stats


def main():
    """
    Main execution function with command line argument support
    """
    parser = argparse.ArgumentParser(description = "Web Content Preprocessor")

    parser.add_argument("--input", "-i", 
                        required = True, 
                        help     = "Input file or directory path",
                       )

    parser.add_argument("--output", "-o", 
                        required = True, 
                        help     = "Output file path",
                       )

    parser.add_argument("--max-tokens", 
                        type    = int, 
                        default = MAX_TOKENS_PER_CHUNK, 
                        help    = "Maximum tokens per chunk",
                       )

    parser.add_argument("--overlap", 
                        type    = int, 
                        default = CHUNK_OVERLAP, 
                        help    = "Overlap tokens between chunks",
                       )

    parser.add_argument("--min-length", 
                        type    = int, 
                        default = MIN_CHUNK_LENGTH, 
                        help    = "Minimum chunk length",
                       )

    parser.add_argument("--language", 
                        default = LANGUAGE, 
                        help    = "Target language",
                       )

    parser.add_argument("--verbose", "-v", 
                        action = "store_true", 
                        help   = "Enable verbose logging",
                       )

    parser.add_argument("--directory", "-d", 
                        action = "store_true", 
                        help   = "Process directory instead of single file",
                       )
    
    args         = parser.parse_args()
    
    # Initialize preprocessor
    preprocessor = Preprocessor(max_tokens    = args.max_tokens,
                                overlap       = args.overlap,
                                min_chunk_len = args.min_length,
                                skip_phrases  = SKIP_PHRASES,
                                language      = args.language,
                                verbose       = args.verbose,
                               )
    
    # Process input
    if args.directory:
        chunk_count = preprocessor.preprocess_directory(args.input, 
                                                        args.output,
                                                       )
    
    else:
        chunk_count = preprocessor.preprocess_jsonl_file(args.input, 
                                                         args.output,
                                                        )
    
    # Print statistics
    if args.verbose:
        stats = preprocessor.get_processing_stats()
        print(f"\nProcessing Statistics:")
        print(f"Total chunks generated: {chunk_count}")
        print(f"Unique content hashes: {stats['utils']['unique_content_hashes']}")


if __name__ == "__main__":
    # Default execution for backward compatibility
    if (len(os.sys.argv) == 1):
        preprocessor = Preprocessor(verbose = True)
        
        # For JSONL files
        input_file   = "../data/scraped_data/itobuz_scraped_data.jsonl"
        output_file  = "../data/preprocessed_data/itobuz_preprocessed_chunks.jsonl"
        
        preprocessor.preprocess_jsonl_file(input_file  = input_file, 
                                           output_file = output_file,
                                          )
    
    else:
        main()