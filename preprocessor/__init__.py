# Dependencies
from .core.utils import Utils
from .core.text_cleaner import TextCleaner
from .core.tag_extractor import TagExtractor
from .core.chunk_builder import ChunkBuilder
from .core.topic_extractor import TopicExtractor
from .core.language_detector import LanguageDetector
from .core.content_categorizer import ContentCategorizer
from .core.named_entity_recognition import NamedEntityRecognizer



__version__ = "1.0.0"

__all__     = ["ChunkBuilder",
               "ContentCategorizer", 
               "LanguageDetector",
               "NamedEntityRecognizer",
               "TagExtractor",
               "TextCleaner",
               "TopicExtractor",
               "Utils",
              ]