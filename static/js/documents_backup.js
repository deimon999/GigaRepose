// Documents Management for new UI structure
const uploadArea = document.getElementById('"'"'uploadArea'"'"');
const fileInput = document.getElementById('"'"'fileInput'"'"');
const documentsList = document.getElementById('"'"'documentsList'"'"');

// Load documents when panel opens
document.addEventListener('"'"'DOMContentLoaded'"'"', () => {
    loadDocuments();
});

// Upload area click to trigger file input
uploadArea.addEventListener('"'"'click'"'"', (e) => {
    if (e.target.tagName !== '"'"'INPUT'"'"') {
        fileInput.click();
    }
});

// Drag and drop handlers
uploadArea.addEventListener('"'"'dragover'"'"', (e) => {
    e.preventDefault();
    uploadArea.classList.add('"'"'dragover'"'"');
});

uploadArea.addEventListener('"'"'dragleave'"'"', () => {
    uploadArea.classList.remove('"'"'dragover'"'"');
});

uploadArea.addEventListener('"'"'drop'"'"', async (e) => {
    e.preventDefault();
    uploadArea.classList.remove('"'"'dragover'"'"');
    
    const files = Array.from(e.dataTransfer.files).filter(f => f.type === '"'"'application/pdf'"'"');
    
    for (let file of files) {
        await uploadFile(file);
    }
    
    loadDocuments();
});

// File selection
fileInput.addEventListener('"'"'change'"'"', async (e) => {
    const files = e.target.files;
    if (files.length === 0) return;
    
    for (let file of files) {
        await uploadFile(file);
    }
    
    fileInput.value = '"'"''"'"';
    loadDocuments();
});

// Upload file function
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('"'"'file'"'"', file);
    
    showNotification(` Uploading ${file.name}...`, '"'"'info'"'"');
    
    try {
        const response = await fetch('"'"'/upload'"'"', {
            method: '"'"'POST'"'"',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification(` ${file.name} uploaded successfully`, '"'"'success'"'"');
        } else {
            let errorMsg = data.error || '"'"'Upload failed'"'"';
            if (errorMsg.includes('"'"'Permission denied'"'"')) {
                errorMsg = `Cannot upload "${file.name}" - file may be open. Close and try again.`;
            }
            showNotification(` ${errorMsg}`, '"'"'error'"'"');
        }
    } catch (error) {
        showNotification(` Upload failed: ${error.message}`, '"'"'error'"'"');
        console.error('"'"'Upload error:'"'"', error);
    }
}

// Load documents
async function loadDocuments() {
    documentsList.innerHTML = '"'"'<p style="text-align:center;color:var(--text-secondary);padding:20px;">Loading...</p>'"'"';
    
    try {
        const response = await fetch('"'"'/documents'"'"');
        const data = await response.json();
        
        if (data.documents.length === 0) {
            documentsList.innerHTML = '"'"'<p style="text-align:center;color:var(--text-secondary);padding:40px;">No documents<br></p>'"'"';
            return;
        }
        
        documentsList.innerHTML = '"'"''"'"';
        
        data.documents.forEach(doc => {
            const docItem = createDocumentItem(doc);
            documentsList.appendChild(docItem);
        });
        
    } catch (error) {
        documentsList.innerHTML = '"'"'<p style="text-align:center;color:#ef4444;padding:20px;">Error loading</p>'"'"';
        console.error(error);
    }
}

// Create document item
function createDocumentItem(doc) {
    const item = document.createElement('"'"'div'"'"');
    item.className = '"'"'document-item'"'"';
    
    const formatSize = (bytes) => {
        if (bytes < 1024) return bytes + '"'"' B'"'"';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + '"'"' KB'"'"';
        return (bytes / (1024 * 1024)).toFixed(1) + '"'"' MB'"'"';
    };
    
    const formatDate = (isoDate) => {
        const date = new Date(isoDate);
        return date.toLocaleDateString() + '"'"' '"'"' + date.toLocaleTimeString();
    };
    
    item.innerHTML = `
        <div class="document-icon"></div>
        <div class="document-info">
            <div class="document-name">${doc.original_name}</div>
            <div style="font-size:0.8rem;color:var(--text-secondary);margin-top:4px;">
                ${formatSize(doc.size)}  ${formatDate(doc.upload_date)}
            </div>
        </div>
        <div class="document-actions">
            <button class="delete-btn" onclick="deleteDocument(${doc.id})">Delete</button>
        </div>
    `;
    
    return item;
}

// Delete document
async function deleteDocument(docId) {
    if (!confirm('"'"'Delete this document?'"'"')) return;
    
    try {
        const response = await fetch(`/documents/${docId}`, { method: '"'"'DELETE'"'"' });
        const data = await response.json();
        
        if (response.ok) {
            showNotification('"'"' Deleted'"'"', '"'"'success'"'"');
            loadDocuments();
        } else {
            showNotification(` ${data.error}`, '"'"'error'"'"');
        }
    } catch (error) {
        showNotification(` ${error.message}`, '"'"'error'"'"');
    }
}

// Show notification
function showNotification(message, type = '"'"'info'"'"') {
    const notification = document.createElement('"'"'div'"'"');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === '"'"'success'"'"' ? '"'"'#10b981'"'"' : type === '"'"'error'"'"' ? '"'"'#ef4444'"'"' : '"'"'#3b82f6'"'"'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s;
        font-weight: 500;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}
