import os
import sys
import logging
from dotenv import load_dotenv

_DEFAULT_DOCS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'docs'))

load_dotenv()

def load_config():
    config = {
        'cohere_api_key': os.getenv('COHERE_API_KEY'),
        'qdrant_api_key': os.getenv('QDRANT_API_KEY'),
        'qdrant_host': os.getenv('QDRANT_HOST', 'localhost'),
        'qdrant_port': int(os.getenv('QDRANT_PORT', 6333)),
        'docs_directory': os.getenv('DOCS_DIR', _DEFAULT_DOCS_DIR),
        'chunk_size': int(os.getenv('CHUNK_SIZE', 512)),
        'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', 50)),
        'cohere_model': os.getenv('COHERE_MODEL', 'embed-multilingual-v3.0')
    }
    return config


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ingestion.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)
