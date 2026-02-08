import chromadb
import hashlib
from sentence_transformers import SentenceTransformer
import tiktoken

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Initialize embedding model
try:
    embedding_model = SentenceTransformer('all-mpnet-base-v2')
    print("✅ Loaded all-mpnet-base-v2 model")
except Exception as e:
    print(f"⚠️ Could not load all-mpnet-base-v2: {e}")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Using fallback all-MiniLM-L6-v2 model")

def chunk_text(text, chunk_size=500, overlap=100):
    """
    Chunk text into overlapping pieces
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
    except:
        encoding = tiktoken.get_encoding("gpt2")
    
    tokens = encoding.encode(text)
    chunks = []
    
    print(f"📄 Total tokens to chunk: {len(tokens)}")
    
    start = 0
    chunk_count = 0
    
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        
        # Only add if chunk has meaningful content
        if len(chunk_text.strip()) > 50:
            chunks.append(chunk_text)
            chunk_count += 1
        
        start = end - overlap
    
    print(f"✅ Created {chunk_count} chunks")
    return chunks

def create_document_id(text):
    """Create unique ID for document"""
    return hashlib.md5(text.encode()).hexdigest()[:16]

def store_document(text, title, metadata=None):
    """
    Store document in vector database with detailed logging
    """
    try:
        print(f"\n{'='*60}")
        print(f"📝 STORING DOCUMENT: {title}")
        print(f"{'='*60}")
        
        # Verify text is not empty
        if not text or len(text.strip()) < 100:
            raise Exception("Text is too short or empty")
        
        print(f"✅ Text length: {len(text)} characters")
        print(f"✅ Text preview: {text[:200]}...")
        
        # Create document ID
        doc_id = create_document_id(text)
        print(f"✅ Document ID: {doc_id}")
        
        # Get or create collection
        try:
            collection = chroma_client.get_collection(name="documents")
            print("✅ Using existing collection")
        except:
            collection = chroma_client.create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Created new collection")
        
        # Check if already exists
        try:
            existing = collection.get(ids=[doc_id])
            if existing['ids']:
                print(f"ℹ️  Document already exists (ID: {doc_id})")
                print(f"   Existing chunks: {len(existing['ids'])}")
                return doc_id
        except:
            pass
        
        # Chunk the document
        print("\n🔄 Chunking document...")
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        
        if not chunks:
            raise Exception("Chunking failed - no chunks created")
        
        print(f"✅ Successfully created {len(chunks)} chunks")
        
        # Create embeddings
        print(f"\n🔄 Creating embeddings for {len(chunks)} chunks...")
        chunk_embeddings = embedding_model.encode(chunks, show_progress_bar=True).tolist()
        print(f"✅ Created {len(chunk_embeddings)} embeddings")
        
        # Prepare metadata
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        chunk_metadata = [
            {
                "doc_id": doc_id,
                "title": title,
                "chunk_index": i,
                "total_chunks": len(chunks),
                **(metadata or {})
            }
            for i in range(len(chunks))
        ]
        
        # Add to collection
        print(f"\n🔄 Adding {len(chunk_ids)} chunks to ChromaDB...")
        collection.add(
            ids=chunk_ids,
            embeddings=chunk_embeddings,
            documents=chunks,
            metadatas=chunk_metadata
        )
        
        print(f"✅ Successfully stored all chunks!")
        print(f"{'='*60}\n")
        
        return doc_id
        
    except Exception as e:
        print(f"\n❌ ERROR in store_document: {str(e)}")
        print(f"{'='*60}\n")
        raise Exception(f"Error storing document: {str(e)}")

def search_documents(query, doc_id=None, top_k=5):
    """
    Search for relevant document chunks with logging
    """
    try:
        collection = chroma_client.get_collection(name="documents")
        
        print(f"\n🔍 SEARCH: '{query}'")
        if doc_id:
            print(f"   Filtering by doc_id: {doc_id}")
        
        # Create query embedding
        query_embedding = embedding_model.encode([query], show_progress_bar=False).tolist()
        
        # Build where clause
        where_clause = {"doc_id": doc_id} if doc_id else None
        
        # Search
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where=where_clause
        )
        
        if not results['ids'][0]:
            print("❌ No results found")
            return []
        
        print(f"✅ Found {len(results['ids'][0])} results")
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            distance = results['distances'][0][i] if 'distances' in results else 1.0
            
            formatted_results.append({
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": distance
            })
            
            print(f"\n  Result {i+1}:")
            print(f"    Distance: {distance:.3f} {'✅ Good match' if distance < 0.6 else '⚠️ Weak match'}")
            print(f"    Preview: {results['documents'][0][i][:150]}...")
        
        return formatted_results
        
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        raise Exception(f"Error searching documents: {str(e)}")

def delete_document(doc_id):
    """Delete all chunks of a document"""
    try:
        collection = chroma_client.get_collection(name="documents")
        results = collection.get(where={"doc_id": doc_id})
        
        if results['ids']:
            collection.delete(ids=results['ids'])
            print(f"✅ Deleted {len(results['ids'])} chunks for doc {doc_id}")
            return True
        
        return False
        
    except Exception as e:
        raise Exception(f"Error deleting document: {str(e)}")

def get_document_info(doc_id):
    """Get information about a stored document"""
    try:
        collection = chroma_client.get_collection(name="documents")
        results = collection.get(where={"doc_id": doc_id})
        
        if results['ids']:
            metadata = results['metadatas'][0]
            return {
                "doc_id": doc_id,
                "title": metadata.get('title', 'Unknown'),
                "chunks": len(results['ids']),
                "metadata": metadata
            }
        
        return None
        
    except Exception as e:
        return None