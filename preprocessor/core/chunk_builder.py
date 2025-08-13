# Dependencies
import logging
from typing import List
from .utils import Utils
from .text_cleaner import TextCleaner
from nltk.tokenize import sent_tokenize


class ChunkBuilder:
    """
    Handles text chunking operations with overlap and validation
    """
    def __init__(self, max_tokens: int = 512, overlap: int = 50, min_chunk_length: int = 100, skip_phrases: List[str] = None, verbose: bool = False):
        """
        Initialize ChunkBuilder
        
        Arguments:
        ----------
            max_tokens       { int } : Maximum tokens per chunk

            overlap          { int } : Number of tokens to overlap between chunks

            min_chunk_length { int } : Minimum chunk length in characters

            skip_phrases    { list } : List of phrases to skip

            verbose         { bool } : Enable verbose logging
        """
        self.max_tokens       = max_tokens
        self.overlap          = overlap
        self.min_chunk_length = min_chunk_length
        self.verbose          = verbose
        
        # Initialize utility classes
        self.utils            = Utils(verbose = verbose)
        self.text_cleaner     = TextCleaner(skip_phrases = skip_phrases, 
                                            verbose      = verbose,
                                           )
        
        # Setup logging
        logging.basicConfig(level = logging.DEBUG if verbose else logging.INFO)

        self.logger           = logging.getLogger("ChunkBuilder")

    
    def is_valid_chunk(self, chunk: str) -> bool:
        """
        Validate chunk quality and check for duplicates.
        
        Arguments:
        ----------
            chunk { str } : Text chunk to validate
            
        Returns:
        ---------
            { bool }      : True if chunk is valid
        """
        if (not chunk or len(chunk.strip()) < self.min_chunk_length):
            return False
        
        chunk_clean = chunk.strip()
        
        # Check for duplicate content
        if (self.utils.is_duplicate_content(chunk_clean)):
            return False
        
        # Check for skip phrases
        if (self.text_cleaner.contains_skip_phrases(chunk_clean)):
            return False
        
        # Use utility validation
        utility_validity = self.utils.is_valid_content(chunk_clean, self.min_chunk_length)
        
        return utility_validity
    

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlapping content
        
        Arguments:
        ----------
            text { str } : Text to chunk
            
        Returns:
        --------
             { list }    : List of text chunks
        """
        if not text or len(text.strip()) < self.min_chunk_length:
            return []
        
        sentences     = sent_tokenize(text)
        chunks        = list()
        current_chunk = list()
        current_len   = 0
        
        for sentence in sentences:
            # Skip very short or very long sentences that might be noise
            sentence = sentence.strip()
            
            if ((len(sentence) < 10) or (len(sentence) > 1000)):
                continue
            
            tokens = sentence.split()
            
            # If adding this sentence exceeds max tokens, finalize current chunk
            if ((current_len + len(tokens)) > self.max_tokens and current_chunk):
                chunk_text = " ".join(current_chunk)
                
                if (self.is_valid_chunk(chunk_text)):
                    chunks.append(chunk_text)
                
                # Start new chunk with overlap
                if (self.overlap > 0):
                    overlap_tokens = []
                    token_count    = 0
                    
                    # Build overlap from end of current chunk
                    for sent in reversed(current_chunk):
                        sent_tokens = sent.split()
                        
                        if ((token_count + len(sent_tokens)) <= self.overlap):
                            overlap_tokens.extend(sent_tokens)
                            token_count += len(sent_tokens)
                        
                        else:
                            break
                    
                    current_chunk = [" ".join(reversed(overlap_tokens))] if overlap_tokens else []
                    current_len   = len(overlap_tokens)
                
                else:
                    current_chunk = []
                    current_len = 0
            
            current_chunk.append(sentence)
            current_len += len(tokens)
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            
            if self.is_valid_chunk(chunk_text):
                chunks.append(chunk_text)
        
        self.logger.debug(f"Created {len(chunks)} chunks from text")
        
        return chunks
    

    def get_chunk_stats(self, chunks: List[str]) -> dict:
        """
        Get statistics about the generated chunks.
        
        Arguments:
        ----------
            chunks { list } : List of text chunks
            
        Returns:
        --------
               { dict }     : Dictionary with chunk statistics
        """
        if not chunks:
            return {"total_chunks" : 0}
        
        chunk_lengths = [len(chunk) for chunk in chunks]
        token_counts  = [len(chunk.split()) for chunk in chunks]

        chunk_stats   =  {"total_chunks"     : len(chunks),
                          "avg_chunk_length" : sum(chunk_lengths) / len(chunks),
                          "min_chunk_length" : min(chunk_lengths),
                          "max_chunk_length" : max(chunk_lengths),
                          "avg_token_count"  : sum(token_counts) / len(chunks),
                          "min_token_count"  : min(token_counts),
                          "max_token_count"  : max(token_counts),
                         }
        
        return
    

    def reset_state(self):
        """
        Reset the chunk builder state (useful for processing multiple documents)
        """
        self.utils.reset_duplicate_tracking()
        self.logger.info("Reset chunk builder state")