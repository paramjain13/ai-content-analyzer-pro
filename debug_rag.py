import chromadb
from document_store import create_document_id

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

try:
    collection = client.get_collection(name="documents")
    
    # Get all documents
    all_docs = collection.get()
    
    print(f"✅ Total chunks stored: {len(all_docs['ids'])}")
    print(f"✅ Unique documents: {len(set(m.get('doc_id') for m in all_docs['metadatas']))}")
    
    # Show first few chunks
    if all_docs['ids']:
        print("\n📄 Sample chunks:")
        for i in range(min(3, len(all_docs['ids']))):
            print(f"\nChunk {i+1}:")
            print(f"  ID: {all_docs['ids'][i]}")
            print(f"  Title: {all_docs['metadatas'][i].get('title', 'N/A')}")
            print(f"  Section: {all_docs['metadatas'][i].get('section_header', 'N/A')}")
            print(f"  Text preview: {all_docs['documents'][i][:150]}...")
    
    # Test search
    print("\n\n🔍 Testing search for 'DFS':")
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('all-mpnet-base-v2')
    query_embedding = model.encode(["What is DFS?"]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5
    )
    
    if results['ids'][0]:
        print(f"✅ Found {len(results['ids'][0])} results")
        for i, doc in enumerate(results['documents'][0]):
            print(f"\nResult {i+1}:")
            print(f"  Distance: {results['distances'][0][i]:.3f}")
            print(f"  Text: {doc[:200]}...")
    else:
        print("❌ No results found!")
        
except Exception as e:
    print(f"❌ Error: {e}")