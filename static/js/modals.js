// Modal and Notification Utilities

// Show custom modal
function showModal(options) {
    const {
        title = 'Confirm',
        message = 'Are you sure?',
        icon = '❓',
        confirmText = 'Confirm',
        cancelText = 'Cancel',
        onConfirm = () => {},
        onCancel = () => {},
        showCancel = true,
        loading = false
    } = options;

    // Remove existing modal if any
    const existingModal = document.querySelector('.custom-modal');
    if (existingModal) {
        existingModal.remove();
    }

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'custom-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-icon ${loading ? 'loading' : ''}">${icon}</div>
            <div class="modal-title">${title}</div>
            <div class="modal-message">${message}</div>
            <div class="modal-actions">
                ${showCancel ? `<button class="modal-btn modal-btn-secondary" id="modalCancel">${cancelText}</button>` : ''}
                <button class="modal-btn modal-btn-primary" id="modalConfirm">${confirmText}</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Add event listeners
    const confirmBtn = modal.querySelector('#modalConfirm');
    const cancelBtn = modal.querySelector('#modalCancel');

    confirmBtn.addEventListener('click', () => {
        modal.remove();
        onConfirm();
    });

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            modal.remove();
            onCancel();
        });
    }

    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
            onCancel();
        }
    });

    return modal;
}

// Show loading modal
function showLoadingModal(message = 'Processing...') {
    return showModal({
        title: 'Please Wait',
        message: message,
        icon: '⏳',
        confirmText: '',
        showCancel: false,
        loading: true
    });
}

// Show success modal
function showSuccessModal(message, onClose = () => {}) {
    return showModal({
        title: 'Success!',
        message: message,
        icon: '✅',
        confirmText: 'OK',
        showCancel: false,
        onConfirm: onClose
    });
}

// Show error modal
function showErrorModal(message, onClose = () => {}) {
    return showModal({
        title: 'Error',
        message: message,
        icon: '❌',
        confirmText: 'OK',
        showCancel: false,
        onConfirm: onClose
    });
}

// Show toast notification
function showToast(message, type = 'info', duration = 4000) {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close">×</button>
    `;

    container.appendChild(toast);

    // Close button
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    });

    // Auto remove
    if (duration > 0) {
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    return toast;
}

// Export for use in other files
window.showModal = showModal;
window.showLoadingModal = showLoadingModal;
window.showSuccessModal = showSuccessModal;
window.showErrorModal = showErrorModal;
window.showToast = showToast;
