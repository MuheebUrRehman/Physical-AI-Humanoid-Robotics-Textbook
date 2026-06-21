import pytest
from ingest_book import create_cli_parser, validate_input_parameters


class TestCLIParser:
    def test_parser_created(self):
        parser = create_cli_parser()
        assert parser is not None

    def test_parser_defaults(self):
        parser = create_cli_parser()
        args = parser.parse_args([])
        assert args.chunk_size == 512
        assert args.chunk_overlap == 50
        assert args.qdrant_host == "localhost"
        assert args.qdrant_port == 6333
        assert args.cohere_model == "embed-multilingual-v3.0"
        assert args.collection_name == "book_vectors"
        assert args.batch_size == 100
        assert args.vector_size == 1024


class TestValidateInputParameters:
    def test_valid_args(self):
        class MockArgs:
            docs_dir = "./my-website/docs"
            chunk_size = 512
            chunk_overlap = 50
            qdrant_host = "localhost"
            qdrant_port = 6333
            cohere_model = "embed-multilingual-v3.0"
            collection_name = "book_vectors"
            batch_size = 100

        assert validate_input_parameters(MockArgs(), skip_dir_check=True) is True

    def test_invalid_chunk_size_negative(self):
        class MockArgs:
            docs_dir = "./my-website/docs"
            chunk_size = -1
            chunk_overlap = 50
            qdrant_host = "localhost"
            qdrant_port = 6333
            cohere_model = "embed-multilingual-v3.0"
            collection_name = "book_vectors"
            batch_size = 100

        with pytest.raises(ValueError):
            validate_input_parameters(MockArgs(), skip_dir_check=True)

    def test_invalid_chunk_overlap_negative(self):
        class MockArgs:
            docs_dir = "./my-website/docs"
            chunk_size = 100
            chunk_overlap = -5
            qdrant_host = "localhost"
            qdrant_port = 6333
            cohere_model = "embed-multilingual-v3.0"
            collection_name = "book_vectors"
            batch_size = 100

        with pytest.raises(ValueError):
            validate_input_parameters(MockArgs(), skip_dir_check=True)

    def test_chunk_overlap_ge_chunk_size(self):
        class MockArgs:
            docs_dir = "./my-website/docs"
            chunk_size = 50
            chunk_overlap = 50
            qdrant_host = "localhost"
            qdrant_port = 6333
            cohere_model = "embed-multilingual-v3.0"
            collection_name = "book_vectors"
            batch_size = 100

        with pytest.raises(ValueError, match="overlap must be less than chunk size"):
            validate_input_parameters(MockArgs(), skip_dir_check=True)

    def test_invalid_port_too_high(self):
        class MockArgs:
            docs_dir = "./my-website/docs"
            chunk_size = 512
            chunk_overlap = 50
            qdrant_host = "localhost"
            qdrant_port = 99999
            cohere_model = "embed-multilingual-v3.0"
            collection_name = "book_vectors"
            batch_size = 100

        with pytest.raises(ValueError, match="1 and 65535"):
            validate_input_parameters(MockArgs(), skip_dir_check=True)

    def test_invalid_collection_name_empty(self):
        class MockArgs:
            docs_dir = "./my-website/docs"
            chunk_size = 512
            chunk_overlap = 50
            qdrant_host = "localhost"
            qdrant_port = 6333
            cohere_model = "embed-multilingual-v3.0"
            collection_name = ""
            batch_size = 100

        with pytest.raises(ValueError):
            validate_input_parameters(MockArgs(), skip_dir_check=True)
