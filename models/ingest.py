import os
from tqdm import tqdm
from dotenv import load_dotenv
import glob
from pathlib import Path

# Import Pinecone with proper error handling
try:
    from pinecone.grpc import PineconeGRPC as Pinecone
    from pinecone import ServerlessSpec
except ImportError:
    try:
        from pinecone import Pinecone, ServerlessSpec
    except ImportError:
        print("Warning: Pinecone not available. Install with: pip install pinecone")
        Pinecone = None
        ServerlessSpec = None

# Import sentence transformers with lazy loading
SentenceTransformer = None

# Import langchain components with fallback
try:
    from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    print("Warning: langchain_community not available. Install with: pip install langchain-community langchain-text-splitters")
    DirectoryLoader = None
    TextLoader = None
    PyPDFLoader = None
    RecursiveCharacterTextSplitter = None

load_dotenv()

class DocumentIngestor:
    def __init__(self):
        global SentenceTransformer
        
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = "jarvis-index"
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        
        # Initialize embedding model (lazy loading)
        print("Loading embedding model...")
        try:
            if SentenceTransformer is None:
                from sentence_transformers import SentenceTransformer as ST
                SentenceTransformer = ST
            self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load sentence transformers: {e}")
            self.embedder = None
        
        # Create or get index
        self._setup_index()
    
    def _setup_index(self):
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            print(f"✓ Index '{self.index_name}' created successfully")
        else:
            print(f"✓ Using existing index: {self.index_name}")
        
        self.index = self.pc.Index(self.index_name)
    
    def ingest_documents(self, data_dir="data"):
        """Ingest documents from a directory"""
        if DirectoryLoader is None or RecursiveCharacterTextSplitter is None:
            print("Error: langchain components not available. Please install:")
            print("pip install langchain-community langchain-text-splitters")
            return
            
        if not os.path.exists(data_dir):
            print(f"Creating data directory: {data_dir}")
            os.makedirs(data_dir)
            print("Please add PDF or TXT files to the data/ directory and run again")
            return
        
        # Load documents (both TXT and PDF)
        print(f"Loading documents from {data_dir}...")
        documents = []
        
        # Load TXT files
        try:
            txt_loader = DirectoryLoader(
                data_dir,
                glob="**/*.txt",
                loader_cls=TextLoader,
                show_progress=True
            )
            txt_docs = txt_loader.load()
            documents.extend(txt_docs)
            print(f"Loaded {len(txt_docs)} TXT files")
        except Exception as e:
            print(f"Note: Could not load TXT files: {e}")
        
        # Load PDF files
        try:
            pdf_loader = DirectoryLoader(
                data_dir,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader,
                show_progress=True
            )
            pdf_docs = pdf_loader.load()
            documents.extend(pdf_docs)
            print(f"Loaded {len(pdf_docs)} PDF files")
        except Exception as e:
            print(f"Note: Could not load PDF files: {e}")
        
        if not documents:
            print("No documents found. Add PDF or TXT files to the data/ directory")
            return
        
        print(f"Loaded {len(documents)} documents")
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Split into {len(chunks)} chunks")
        
        # Generate embeddings and upsert to Pinecone
        print("Generating embeddings and uploading to Pinecone...")
        batch_size = 100
        
        for i in tqdm(range(0, len(chunks), batch_size)):
            batch = chunks[i:i + batch_size]
            
            # Generate embeddings
            texts = [doc.page_content for doc in batch]
            embeddings = self.embedder.encode(texts).tolist()
            
            # Prepare vectors for upsert
            vectors = []
            for j, (text, embedding) in enumerate(zip(texts, embeddings)):
                vector_id = f"doc_{i+j}"
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {"text": text}
                })
            
            # Upsert to Pinecone
            self.index.upsert(vectors=vectors)
        
        print(f"✓ Successfully ingested {len(chunks)} chunks to Pinecone!")

if __name__ == "__main__":
    ingestor = DocumentIngestor()
    ingestor.ingest_documents()
