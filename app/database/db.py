import os
import yaml
from tqdm import tqdm
import chromadb

from app.database.get_embedding_function import get_embedding_function


CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def update_data_base(db_path: str, data_path: str):
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection("token-kb", embedding_function=get_embedding_function())
    data = load_data(data_path)

    print(f"\nDocuments found: {len(data)}\n")
    added, skipped = add_documents_to_collection(collection, data)
    print(f"\nUpdate complete. Added: {added}, Skipped (already exists): {skipped}\n")


def reload_data_base(db_path: str, data_path: str):
    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)

    try:
        client.delete_collection("token-kb")
    except Exception:
        pass

    collection = client.get_or_create_collection("token-kb", embedding_function=get_embedding_function())
    data = load_data(data_path)

    print(f"\nDocuments found: {len(data)}\n")
    added, _ = add_documents_to_collection(collection, data, skip_existing=False)
    print(f"\nReload complete. All chunks added: {added}\n")


def query_rag(
    db_path: str,
    query: str,
    collection_name: str = "token-kb",
    n_results: int = 5
) -> list[dict]:
    client = chromadb.PersistentClient(path=db_path)

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=get_embedding_function(),
    )

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return [
        {
            "id": result_id,
            "document": document,
            "metadata": metadata
        }
        for result_id, document, metadata in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0]
        )
    ]


def add_documents_to_collection(collection, data: list[dict], skip_existing: bool = True) -> tuple[int, int]:
    added = 0
    skipped = 0

    for doc in tqdm(data, desc="Processing documents", unit="doc"):
        chunks = split_text_into_chunks(doc["text"])
        doc_location = doc["location"]

        for idx, chunk in enumerate(chunks):
            uid = f'{doc_location}_{idx}'

            if skip_existing:
                existing = collection.get(ids=[uid])
                if existing['ids']:
                    skipped += 1
                    continue

            collection.add(
                documents=[chunk],
                metadatas=[{
                    "source": doc["source"],
                    "location": doc["location"],
                    "type": doc["type"],
                    "chunk_index": idx
                }],
                ids=[uid]
            )
            added += 1

    return added, skipped


def load_data(data_path: str) -> list[dict]:
    root_path = os.path.join(data_path, "root.yaml")
    with open(root_path, "r", encoding="utf-8") as f:
        root_config = yaml.safe_load(f)

    all_docs = []

    for import_file in root_config.get("imports", []):
        import_path = os.path.join(data_path, import_file)
        with open(import_path, "r", encoding="utf-8") as f:
            import_config = yaml.safe_load(f)

        docs = import_config.get("docs", {})
        for doc_info in docs.values():
            location = doc_info["location"]
            doc_type = doc_info["type"]
            source_file = doc_info["source"]

            full_path = os.path.join(os.path.dirname(import_path), source_file)
            if not os.path.exists(full_path):
                print(f"File not found: {full_path}")
                continue

            with open(full_path, "r", encoding="utf-8") as tf:
                text = tf.read()

            all_docs.append({
                "source": source_file,
                "location": location,
                "type": doc_type,
                "text": text
            })

    return all_docs


def split_text_into_chunks(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


if __name__ == "__main__":
    pass
    #print(query_rag("../../chroma", "ЦФА - что это"))
    #update_data_base("../../chroma", "../../data")