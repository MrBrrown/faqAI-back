import chromadb.utils.embedding_functions


def get_embedding_function():
    return chromadb.utils.embedding_functions.DefaultEmbeddingFunction()