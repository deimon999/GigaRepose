# How to Add Knowledge to Jarvis

## Step 1: Add Your PDF Files

1. Copy your PDF files into the `data/` folder:
   ```
   E:\NoSql Project\Jarvis\jarvis-mvp\data\
   ```

2. Supported formats:
   - PDF files (`.pdf`)
   - Text files (`.txt`)

## Step 2: Create Pinecone Index

Before ingesting, you need to create a Pinecone index:

1. Go to https://app.pinecone.io/
2. Log in with your account
3. Click "Create Index"
4. Settings:
   - **Name**: `jarvis-index`
   - **Dimensions**: `384`
   - **Metric**: `cosine`
   - **Cloud**: AWS
   - **Region**: us-east-1 (or your preferred region)
5. Click "Create Index"

## Step 3: Ingest Documents

Run the ingestion script:

```powershell
cd "E:\NoSql Project\Jarvis\jarvis-mvp"
.venv\Scripts\Activate.ps1
python app/ingest.py
```

This will:
- Load all PDF and TXT files from `data/`
- Split them into chunks (1000 chars with 200 overlap)
- Generate embeddings using sentence-transformers
- Upload to Pinecone

## Step 4: Chat with Your Documents

Once ingested, Jarvis will automatically retrieve relevant context from your PDFs when you chat!

Example:
- You: "What does the document say about machine learning?"
- Jarvis: *Retrieves relevant sections from your PDFs and answers based on that context*

## Updating Documents

To add more documents:
1. Add new PDFs to `data/` folder
2. Run `python app/ingest.py` again
3. New documents will be added to existing index

## Troubleshooting

**"No module named 'pinecone'"**
- Run: `pip install --upgrade pinecone-client`

**"Index 'jarvis-index' not found"**
- Create the index in Pinecone dashboard first (see Step 2)

**"Could not load PDF files"**
- Make sure pypdf is installed: `pip install pypdf`
