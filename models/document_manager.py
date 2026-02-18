import os
from pathlib import Path
from datetime import datetime
import json

class DocumentManager:
    """Manage uploaded documents"""
    
    def __init__(self, data_dir="data", metadata_file="data/documents.json"):
        self.data_dir = Path(data_dir)
        self.metadata_file = Path(metadata_file)
        self.data_dir.mkdir(exist_ok=True)
        
        # Load or create metadata
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"documents": []}
            self._save_metadata()
    
    def _save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def add_document(self, file_path, original_name, file_size):
        """Add document metadata"""
        doc_info = {
            "id": len(self.metadata["documents"]) + 1,
            "filename": Path(file_path).name,
            "original_name": original_name,
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "path": str(file_path),
            "status": "uploaded"
        }
        self.metadata["documents"].append(doc_info)
        self._save_metadata()
        return doc_info
    
    def get_all_documents(self):
        """Get list of all documents"""
        return self.metadata["documents"]
    
    def delete_document(self, doc_id):
        """Delete a document"""
        for i, doc in enumerate(self.metadata["documents"]):
            if doc["id"] == doc_id:
                # Delete file
                file_path = Path(doc["path"])
                if file_path.exists():
                    file_path.unlink()
                # Remove from metadata
                self.metadata["documents"].pop(i)
                self._save_metadata()
                return True
        return False
    
    def get_document_count(self):
        """Get total document count"""
        return len(self.metadata["documents"])
