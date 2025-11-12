import os

# Import Pinecone with proper error handling
try:
    from pinecone.grpc import PineconeGRPC as Pinecone
except ImportError:
    try:
        from pinecone import Pinecone
    except ImportError:
        print("Warning: Pinecone not available. Install with: pip install pinecone")
        Pinecone = None

class Retriever:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = "jarvis-index"
        self.embedder = None
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        
        # Initialize embedding model (lazy loading)
        self._init_embedder()
        
        # Get index (will create later if needed)
        try:
            self.index = self.pc.Index(self.index_name)
            print(f"✓ Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            print(f"⚠ Could not connect to Pinecone index '{self.index_name}': {e}")
            print(f"You may need to create the index first with dimension=384")
            self.index = None
    
    def _init_embedder(self):
        """Lazy load the sentence transformer model"""
        if self.embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')
            except Exception as e:
                print(f"⚠ Could not load sentence-transformers: {e}")
                print("Document search will not be available")
                self.embedder = None
    
    def get_relevant_documents(self, query, top_k=3):
        """Retrieve relevant documents from Pinecone"""
        if not self.index or not self.embedder:
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.embedder.encode(query).tolist()
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract text from results
            documents = []
            if hasattr(results, 'matches'):
                for match in results.matches:
                    if hasattr(match, 'metadata') and match.metadata and 'text' in match.metadata:
                        documents.append(match.metadata['text'])
            
            return documents
            
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            return []
