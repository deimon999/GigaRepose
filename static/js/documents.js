// Documents Management
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const documentsList = document.getElementById('documentsList');

// Don't auto-load on page load, wait for panel to open
// Load documents when panel opens (called from app.js)

// Upload area click to trigger file input
if (uploadArea) {
    uploadArea.addEventListener('click', (e) => {
        if (e.target.tagName !== 'INPUT') {
            fileInput.click();
        }
    });

    // Drag and drop handlers
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', async (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf' || f.name.endsWith('.txt'));
        
        for (let file of files) {
            await uploadFile(file);
        }
        
        loadDocuments();
    });
}

// File selection
if (fileInput) {
    fileInput.addEventListener('change', async (e) => {
        const files = e.target.files;
        if (files.length === 0) return;
        
        for (let file of files) {
            await uploadFile(file);
        }
        
        fileInput.value = '';
        loadDocuments();
    });
}

// Upload file function
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showNotification(`📤 Uploading ${file.name}...`, 'info');
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification(`✅ ${file.name} uploaded successfully`, 'success');
        } else {
            let errorMsg = data.error || 'Upload failed';
            if (errorMsg.includes('Permission denied')) {
                errorMsg = `Cannot upload "${file.name}" - file may be open. Close and try again.`;
            }
            showNotification(`❌ ${errorMsg}`, 'error');
        }
    } catch (error) {
        showNotification(`❌ Upload failed: ${error.message}`, 'error');
        console.error('Upload error:', error);
    }
}

// Load documents
async function loadDocuments() {
    if (!documentsList) return;
    
    documentsList.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:20px;">Loading...</p>';
    
    try {
        const response = await fetch('/documents');
        const data = await response.json();
        
        if (!data.documents || data.documents.length === 0) {
            documentsList.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:40px;">No documents uploaded yet<br><small>Upload PDF or TXT files to get started</small></p>';
            return;
        }
        
        documentsList.innerHTML = '';
        
        data.documents.forEach(doc => {
            const docItem = createDocumentItem(doc);
            documentsList.appendChild(docItem);
        });
    } catch (error) {
        console.error('Error loading documents:', error);
        documentsList.innerHTML = '<p style="text-align:center;color:#ef4444;">Error loading documents</p>';
    }
}

// Create document item element
function createDocumentItem(doc) {
    const item = document.createElement('div');
    item.className = 'document-item';
    
    const uploadDate = doc.upload_date || doc.uploaded_at;
    const displayDate = uploadDate ? new Date(uploadDate).toLocaleDateString() : '';
    
    item.innerHTML = `
        <div class="document-icon">📄</div>
        <div class="document-info">
            <div class="document-name">${escapeHtml(doc.original_name || doc.filename || doc.name)}</div>
            <div style="font-size:0.8rem;color:var(--text-secondary);">
                ${displayDate}
            </div>
        </div>
        <div class="document-actions">
            <button onclick="deleteDocument(${doc.id}, '${escapeHtml(doc.original_name || doc.filename)}')" class="delete-btn">Delete</button>
        </div>
    `;
    
    return item;
}

// Delete document
async function deleteDocument(docId, filename) {
    if (!confirm(`Delete "${filename}"?`)) return;
    
    try {
        const response = await fetch(`/documents/${docId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification(`✅ Document deleted`, 'success');
            loadDocuments();
        } else {
            showNotification(`❌ ${data.error || 'Delete failed'}`, 'error');
        }
    } catch (error) {
        showNotification(`❌ Error: ${error.message}`, 'error');
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show notification
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Use toast notifications if available
    if (typeof showToast === 'function') {
        showToast(message, type);
    }
}

// Re-ingest all documents to Pinecone
async function reIngestDocuments() {
    console.log('reIngestDocuments function called');
    
    showModal({
        title: 'Re-ingest Documents?',
        message: 'This will ingest all uploaded documents into the vector database. This may take a few minutes.',
        icon: '🔄',
        confirmText: 'Start Ingesting',
        cancelText: 'Cancel',
        onConfirm: async () => {
            console.log('User confirmed, starting re-ingest...');
            
            // Show loading modal
            const loadingModal = showLoadingModal('Ingesting documents... Please wait.');
            
            try {
                console.log('Fetching /ingest-all endpoint...');
                const response = await fetch('/ingest-all', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                console.log('Response received:', response.status);
                const data = await response.json();
                console.log('Response data:', data);
                
                // Remove loading modal
                loadingModal.remove();
                
                if (response.ok) {
                    showSuccessModal('All documents have been ingested successfully! You can now search across all uploaded documents.');
                    showToast('Documents ingested successfully!', 'success');
                } else {
                    showErrorModal(data.error || 'Ingestion failed. Please check your Pinecone configuration and try again.');
                    showToast(data.error || 'Ingestion failed', 'error');
                }
            } catch (error) {
                console.error('Catch block error:', error);
                // Remove loading modal
                loadingModal.remove();
                showErrorModal(`Error during ingestion: ${error.message}`);
                showToast(`Error: ${error.message}`, 'error');
            }
        },
        onCancel: () => {
            console.log('User cancelled ingestion');
        }
    });
}

// Setup function called when documents panel opens
let documentsListenersSetup = false;

function setupDocumentsEventListeners() {
    console.log('Setting up documents listeners...');
    
    // Always reload documents when panel opens
    loadDocuments();
    
    // Only set up event listeners once
    if (documentsListenersSetup) {
        console.log('Documents listeners already set up, just reloaded data');
        return;
    }
    documentsListenersSetup = true;
}

// Export to global scope
window.setupDocumentsEventListeners = setupDocumentsEventListeners;
window.reIngestDocuments = reIngestDocuments;
window.deleteDocument = deleteDocument;
