// DeepFake Detector - Version 1.4
// Last updated: Added multi-select comparison picker and polished video workflows

let currentFile = null;

// Drag and drop functionality
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--accent-color)';
    uploadArea.style.background = 'rgba(78, 205, 196, 0.1)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'var(--border-color)';
    uploadArea.style.background = 'transparent';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--border-color)';
    uploadArea.style.background = 'transparent';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    currentFile = file;
    const fileType = file.type;
    
    // Hide upload area, show preview
    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('previewSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    
    const previewImage = document.getElementById('previewImage');
    const previewVideo = document.getElementById('previewVideo');
    
    if (fileType.startsWith('image/')) {
        previewImage.style.display = 'block';
        previewVideo.style.display = 'none';
        previewImage.src = URL.createObjectURL(file);
    } else if (fileType.startsWith('video/')) {
        previewImage.style.display = 'none';
        previewVideo.style.display = 'block';
        previewVideo.src = URL.createObjectURL(file);
    }
}

function resetUpload() {
    currentFile = null;
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('previewSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    fileInput.value = '';
}

async function analyzeMedia() {
    if (!currentFile) return;
    
    // Show loading overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    
    const formData = new FormData();
    formData.append('file', currentFile);
    
    try {
        // Check if heatmap mode is active
        const endpoint = window.heatmapMode ? '/heatmap' : '/upload';
        
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Analysis result:', result); // Debug log
        
        if (result.error) {
            showCustomAlert(
                'Processing Error',
                result.error,
                'warning'
            );
            return;
        }
        
        // Display heatmap or regular results
        if (window.heatmapMode) {
            displayHeatmapResults(result);
            window.heatmapMode = false; // Reset mode
        } else {
            displayResults(result);
        }
    } catch (error) {
        console.error('Error details:', error);
        showCustomAlert(
            'Analysis Error',
            `An error occurred while analyzing the media. ${error.message || 'Please try again or check the file format.'}`,
            'warning'
        );
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

function displayResults(result) {
    try {
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        
        const verdictCard = document.getElementById('verdictCard');
        const verdictLabel = document.getElementById('verdictLabel');
        const verdictIcon = document.getElementById('verdictIcon');
        const confidenceFill = document.getElementById('confidenceFill');
        const confidenceText = document.getElementById('confidenceText');
        
        // Set verdict
        const prediction = result.overall_prediction || 'UNKNOWN';
        const isReal = prediction === 'REAL';
        const isUncertain = prediction === 'UNCERTAIN';
        
        verdictCard.className = 'verdict-card ' + (isUncertain ? 'uncertain' : (isReal ? 'real' : 'fake'));
        verdictLabel.textContent = prediction;
        
        // Update icon
        if (isReal) {
            verdictIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
        } else if (isUncertain) {
            verdictIcon.innerHTML = '<i class="fas fa-question-circle"></i>';
        } else {
            verdictIcon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        }
        
        // Set confidence
        const confidence = result.overall_confidence || 0;
        confidenceFill.style.width = confidence + '%';
        confidenceText.textContent = `Confidence: ${confidence.toFixed(1)}%`;
        
        // Set details
        document.getElementById('facesCount').textContent = result.faces_detected || result.frames_analyzed || '-';
        document.getElementById('framesCount').textContent = result.frames_analyzed || '-';
        document.getElementById('detectionScore').textContent = 
            result.prediction_score ? (result.prediction_score * 100).toFixed(1) + '%' : '-';
        
        // Show processed image if available
        if (result.processed_image) {
            document.getElementById('processedImageContainer').style.display = 'block';
            document.getElementById('processedImage').src = 'data:image/jpeg;base64,' + result.processed_image;
        } else {
            document.getElementById('processedImageContainer').style.display = 'none';
        }
        
        // Show face results table if available
        if (result.face_results && result.face_results.length > 0) {
            document.getElementById('faceResults').style.display = 'block';
            const tbody = document.getElementById('faceResultsBody');
            tbody.innerHTML = '';
            
            result.face_results.forEach(face => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${face.face_number}</td>
                    <td><span class="prediction-badge ${face.prediction.toLowerCase()}">${face.prediction}</span></td>
                    <td>${face.confidence.toFixed(1)}%</td>
                    <td>${(face.score * 100).toFixed(1)}%</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            document.getElementById('faceResults').style.display = 'none';
        }
    } catch (error) {
        console.error('Error displaying results:', error);
        showCustomAlert(
            'Display Error',
            `Failed to display results: ${error.message}. Please refresh the page and try again.`,
            'warning'
        );
    }
}

async function showStats() {
    try {
        const response = await fetch('/stats');
        const stats = await response.json();
        
        document.getElementById('trainSamples').textContent = stats.dataset_info.train_samples;
        document.getElementById('valSamples').textContent = stats.dataset_info.val_samples;
        document.getElementById('testSamples').textContent = stats.dataset_info.test_samples;
        document.getElementById('totalVideos').textContent = stats.dataset_info.total_videos;
        document.getElementById('realVideos').textContent = stats.dataset_info.real_videos;
        document.getElementById('fakeVideos').textContent = stats.dataset_info.fake_videos;
        document.getElementById('modelStatus').textContent = stats.model_loaded ? '✓ Loaded' : '✗ Not Loaded';
        document.getElementById('detectionThreshold').textContent = stats.detection_threshold.toFixed(2);
        
        // Update threshold slider
        const threshold = stats.detection_threshold;
        document.getElementById('thresholdSlider').value = threshold * 100;
        document.getElementById('thresholdValue').textContent = threshold.toFixed(2);
        
        document.getElementById('statsModal').style.display = 'flex';
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Threshold slider interaction
document.getElementById('thresholdSlider')?.addEventListener('input', (e) => {
    const value = e.target.value / 100;
    document.getElementById('thresholdValue').textContent = value.toFixed(2);
});

async function updateThreshold() {
    const threshold = document.getElementById('thresholdSlider').value / 100;
    
    try {
        const response = await fetch('/set-threshold', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ threshold: threshold })
        });
        
        const result = await response.json();
        
        showCustomAlert(
            'Threshold Updated',
            `${result.message}\n\nLower threshold = More sensitive to fakes\nHigher threshold = More conservative`,
            'success'
        );
        
        // Update display
        document.getElementById('detectionThreshold').textContent = result.threshold.toFixed(2);
    } catch (error) {
        console.error('Error updating threshold:', error);
        showCustomAlert('Update Failed', 'Failed to update threshold', 'warning');
    }
}

function closeStats() {
    document.getElementById('statsModal').style.display = 'none';
}

// Close modal when clicking outside
document.getElementById('statsModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'statsModal') {
        closeStats();
    }
});

// Load stats on page load
window.addEventListener('load', () => {
    fetch('/stats')
        .then(response => response.json())
        .then(stats => {
            console.log('Model status:', stats.model_loaded ? 'Loaded' : 'Not loaded');
        })
        .catch(error => console.error('Error:', error));
});

// Advanced Features Functions
function showFeatures() {
    document.getElementById('featuresModal').style.display = 'flex';
}

function closeFeatures() {
    document.getElementById('featuresModal').style.display = 'none';
}

// Display heatmap results
function displayHeatmapResults(result) {
    document.getElementById('resultsSection').style.display = 'block';
    
    // Update verdict card
    const prediction = result.prediction || 'UNKNOWN';
    const isReal = prediction === 'REAL';
    const isUncertain = prediction === 'UNCERTAIN';
    
    const verdictCard = document.getElementById('verdictCard');
    verdictCard.className = 'verdict-card ' + (isUncertain ? 'uncertain' : (isReal ? 'real' : 'fake'));
    
    document.getElementById('verdictLabel').textContent = `${prediction} (Heatmap)`;
    document.getElementById('verdictIcon').innerHTML = isReal ? 
        '<i class="fas fa-check-circle"></i>' : 
        (isUncertain ? '<i class="fas fa-question-circle"></i>' : '<i class="fas fa-exclamation-triangle"></i>');
    
    const confidence = result.confidence || 0;
    document.getElementById('confidenceFill').style.width = confidence + '%';
    document.getElementById('confidenceText').textContent = `Confidence: ${confidence.toFixed(1)}%`;
    
    // Display heatmap image
    if (result.heatmap_image) {
        const previewImage = document.getElementById('previewImage');
        previewImage.src = 'data:image/jpeg;base64,' + result.heatmap_image;
        previewImage.style.display = 'block';
    }
    
    // Add heatmap details to results section
    let faceDetails = document.getElementById('faceDetails');
    if (!faceDetails) {
        // Create the element if it doesn't exist
        faceDetails = document.createElement('div');
        faceDetails.id = 'faceDetails';
        document.getElementById('resultsSection').appendChild(faceDetails);
    }
    
    faceDetails.innerHTML = `
        <div style="background: var(--card-bg); padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h3 style="margin-top: 0;">Attention Heatmap Analysis</h3>
            <p><strong>Raw Score:</strong> ${result.raw_score?.toFixed(4) || 'N/A'}</p>
            <p><strong>Prediction:</strong> ${prediction}</p>
            <p><strong>Confidence:</strong> ${confidence.toFixed(1)}%</p>
            <p style="color: var(--text-muted); font-size: 0.9em; margin: 10px 0 0 0;">
                The heatmap shows regions the model focuses on. Brighter colors indicate areas of higher attention.
            </p>
        </div>
    `;
}

// Display comparison results
function displayComparisonResults(result) {
    document.getElementById('resultsSection').style.display = 'block';
    
    const file1 = result.file1;
    const file2 = result.file2;
    const comparison = result.comparison;
    
    // Update verdict card with comparison summary
    const verdictCard = document.getElementById('verdictCard');
    verdictCard.className = 'verdict-card ' + (comparison.verdict_match ? 'real' : 'fake');
    
    document.getElementById('verdictLabel').textContent = 'Comparison Results';
    document.getElementById('verdictIcon').innerHTML = '<i class="fas fa-balance-scale"></i>';
    
    const avgConf = (file1.confidence + file2.confidence) / 2;
    document.getElementById('confidenceFill').style.width = avgConf + '%';
    document.getElementById('confidenceText').textContent = comparison.summary;
    
    // Display comparison details
    let faceDetails = document.getElementById('faceDetails');
    if (!faceDetails) {
        // Create the element if it doesn't exist
        faceDetails = document.createElement('div');
        faceDetails.id = 'faceDetails';
        document.getElementById('resultsSection').appendChild(faceDetails);
    }
    
    const file1CountLabel = file1.type === 'video' ? 'Frames Analyzed' : 'Faces Detected';
    const file2CountLabel = file2.type === 'video' ? 'Frames Analyzed' : 'Faces Detected';
    const file1CountValue = file1.type === 'video'
        ? (typeof file1.frames_analyzed === 'number' ? file1.frames_analyzed : 0)
        : (typeof file1.faces_detected === 'number' ? file1.faces_detected : 0);
    const file2CountValue = file2.type === 'video'
        ? (typeof file2.frames_analyzed === 'number' ? file2.frames_analyzed : 0)
        : (typeof file2.faces_detected === 'number' ? file2.faces_detected : 0);

    faceDetails.innerHTML = `
        <div style="background: var(--card-bg); padding: 20px; border-radius: 8px; margin-top: 15px;">
            <h3 style="margin-top: 0;">Side-by-Side Comparison</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div style="border: 2px solid ${file1.prediction === 'REAL' ? 'var(--success-color)' : (file1.prediction === 'UNCERTAIN' ? 'orange' : 'var(--danger-color)')}; border-radius: 8px; padding: 15px;">
                    <h4 style="margin-top: 0;">File 1: ${file1.name}</h4>
                    <p style="color: #888; font-size: 0.9em; margin: 5px 0;">Type: ${file1.type}</p>
                    ${file1.processed_image ? `<img src="data:image/jpeg;base64,${file1.processed_image}" style="width: 100%; border-radius: 4px; margin: 10px 0;">` : '<p style="color: #888; font-style: italic;">No preview available</p>'}
                    <p><strong>Prediction:</strong> <span style="color: ${file1.prediction === 'REAL' ? 'var(--success-color)' : (file1.prediction === 'UNCERTAIN' ? 'orange' : 'var(--danger-color)')}">${file1.prediction}</span></p>
                    <p><strong>Confidence:</strong> ${file1.confidence.toFixed(1)}%</p>
                    <p><strong>${file1CountLabel}:</strong> ${file1CountValue}</p>
                </div>
                
                <div style="border: 2px solid ${file2.prediction === 'REAL' ? 'var(--success-color)' : (file2.prediction === 'UNCERTAIN' ? 'orange' : 'var(--danger-color)')}; border-radius: 8px; padding: 15px;">
                    <h4 style="margin-top: 0;">File 2: ${file2.name}</h4>
                    <p style="color: #888; font-size: 0.9em; margin: 5px 0;">Type: ${file2.type}</p>
                    ${file2.processed_image ? `<img src="data:image/jpeg;base64,${file2.processed_image}" style="width: 100%; border-radius: 4px; margin: 10px 0;">` : '<p style="color: #888; font-style: italic;">No preview available</p>'}
                    <p><strong>Prediction:</strong> <span style="color: ${file2.prediction === 'REAL' ? 'var(--success-color)' : (file2.prediction === 'UNCERTAIN' ? 'orange' : 'var(--danger-color)')}">${file2.prediction}</span></p>
                    <p><strong>Confidence:</strong> ${file2.confidence.toFixed(1)}%</p>
                    <p><strong>${file2CountLabel}:</strong> ${file2CountValue}</p>
                </div>
            </div>
            
            <div style="background: rgba(78, 205, 196, 0.1); padding: 15px; border-radius: 8px;">
                <h4 style="margin-top: 0;">Comparison Metrics</h4>
                <p><strong>Verdict Match:</strong> ${comparison.verdict_match ? '✓ Both files have same prediction' : '✗ Different predictions'}</p>
                <p><strong>Confidence Difference:</strong> ${comparison.confidence_difference.toFixed(1)}%</p>
                ${comparison.both_uncertain ? '<p style="color: orange;"><strong>⚠ Both results are uncertain</strong></p>' : ''}
            </div>
        </div>
    `;
}

function activateHeatmap() {
    closeFeatures();
    showCustomAlert(
        'Attention Heatmap Mode Activated',
        'Upload an image, then the system will generate an attention heatmap showing suspicious regions!',
        'info'
    );
    window.heatmapMode = true;
}

function activateBatchMode() {
    closeFeatures();
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'image/*,video/*';
    input.onchange = handleBatchUpload;
    input.click();
}

async function handleBatchUpload(e) {
    const files = e.target.files;
    if (files.length === 0) return;
    
    document.getElementById('loadingOverlay').style.display = 'flex';
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files[]', file);
    }
    
    try {
        const response = await fetch('/batch-upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        displayBatchResults(result);
    } catch (error) {
        console.error('Error:', error);
        showCustomAlert('Batch Error', 'Error processing batch upload', 'warning');
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

function displayBatchResults(result) {
    document.getElementById('resultsSection').style.display = 'block';
    
    let fakeCount = 0;
    let realCount = 0;
    let uncertainCount = 0;
    
    result.results.forEach(r => {
        if (r.overall_prediction === 'FAKE') fakeCount++;
        else if (r.overall_prediction === 'REAL') realCount++;
        else if (r.overall_prediction === 'UNCERTAIN') uncertainCount++;
    });
    
    const verdictLabel = document.getElementById('verdictLabel');
    verdictLabel.textContent = `Batch Analysis: ${result.total_processed} files`;
    
    document.getElementById('facesCount').textContent = result.total_processed;
    document.getElementById('framesCount').textContent = `${fakeCount} Fake / ${uncertainCount} Uncertain / ${realCount} Real`;
    document.getElementById('detectionScore').textContent = ((fakeCount / result.total_processed) * 100).toFixed(1) + '% Fake';
    
    // Show detailed results
    const tbody = document.getElementById('faceResultsBody');
    tbody.innerHTML = '';
    document.getElementById('faceResults').style.display = 'block';
    
    result.results.forEach((r, idx) => {
        const row = document.createElement('tr');
        const prediction = r.overall_prediction || 'ERROR';
        const badgeClass = prediction.toLowerCase();
        
        row.innerHTML = `
            <td>${r.filename || 'File ' + (idx + 1)}</td>
            <td><span class="prediction-badge ${badgeClass}">${prediction}</span></td>
            <td>${r.overall_confidence?.toFixed(1) || 0}%</td>
            <td>${r.faces_detected || r.frames_analyzed || '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

function activateCompareMode() {
    closeFeatures();

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,video/*';
    input.multiple = true;
    input.onchange = async (event) => {
        const files = Array.from(event.target.files);

        if (files.length < 2) {
            showCustomAlert(
                'Select Two Files',
                'Please choose two files (images or videos) to run the comparison.',
                'warning'
            );
            return;
        }

        const [file1, file2] = files;
        document.getElementById('loadingOverlay').style.display = 'flex';

        const formData = new FormData();
        formData.append('file1', file1);
        formData.append('file2', file2);

        try {
            const response = await fetch('/compare', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.error) {
                showCustomAlert('Comparison Error', result.error, 'warning');
                return;
            }

            displayComparisonResults(result);
        } catch (error) {
            console.error('Error:', error);
            showCustomAlert('Comparison Failed', 'Error comparing files', 'warning');
        } finally {
            document.getElementById('loadingOverlay').style.display = 'none';
        }
    };

    input.click();
}

async function activateTemporalMode() {
    closeFeatures();
    
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'video/*';
    input.onchange = async (e) => {
        if (e.target.files.length === 0) return;
        
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        const formData = new FormData();
        formData.append('file', e.target.files[0]);
        
        try {
            const response = await fetch('/temporal-analysis', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            displayTemporalAnalysis(result);
        } catch (error) {
            console.error('Error:', error);
            showCustomAlert('Video Analysis Failed', 'Error analyzing video', 'warning');
        } finally {
            document.getElementById('loadingOverlay').style.display = 'none';
        }
    };
    input.click();
}

let temporalChart = null;

function displayTemporalAnalysis(result) {
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('temporalChart').style.display = 'block';
    
    // Update verdict
    const verdictCard = document.getElementById('verdictCard');
    const isReal = result.overall_prediction === 'REAL';
    verdictCard.className = 'verdict-card ' + (isReal ? 'real' : 'fake');
    document.getElementById('verdictLabel').textContent = result.overall_prediction;
    
    const confidence = ((result.average_prediction > 0.5 ? result.average_prediction : 1 - result.average_prediction) * 100);
    document.getElementById('confidenceFill').style.width = confidence + '%';
    document.getElementById('confidenceText').textContent = `Confidence: ${confidence.toFixed(1)}%`;
    
    // Update temporal stats
    document.getElementById('temporalVariance').textContent = result.temporal_variance.toFixed(4);
    document.getElementById('consistencyScore').textContent = result.consistency_score.toFixed(1);
    document.getElementById('detectedJumps').textContent = result.inconsistency_jumps.length;
    
    // Create chart
    const ctx = document.getElementById('chartCanvas').getContext('2d');
    
    if (temporalChart) {
        temporalChart.destroy();
    }
    
    temporalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: result.frame_numbers,
            datasets: [{
                label: 'Fake Probability',
                data: result.frame_predictions,
                borderColor: 'rgb(255, 71, 87)',
                backgroundColor: 'rgba(255, 71, 87, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Threshold (0.5)',
                data: Array(result.frame_predictions.length).fill(0.5),
                borderColor: 'rgb(78, 205, 196)',
                borderDash: [5, 5],
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        color: '#a0a4b8'
                    },
                    grid: {
                        color: 'rgba(160, 164, 184, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#a0a4b8'
                    },
                    grid: {
                        color: 'rgba(160, 164, 184, 0.1)'
                    }
                }
            }
        }
    });
}

async function showTrainingSamples() {
    try {
        const response = await fetch('/training-samples');
        const samples = await response.json();
        
        const fakeGrid = document.getElementById('fakeSamplesGrid');
        const realGrid = document.getElementById('realSamplesGrid');
        
        fakeGrid.innerHTML = '';
        realGrid.innerHTML = '';
        
        // Display fake samples
        samples.fake_samples.slice(0, 12).forEach(sample => {
            const div = document.createElement('div');
            div.className = 'sample-item';
            div.innerHTML = `
                <img src="${sample.image_data}" alt="Fake sample">
                <div class="sample-label">ID: ${sample.video_id}</div>
            `;
            fakeGrid.appendChild(div);
        });
        
        // Display real samples
        samples.real_samples.slice(0, 12).forEach(sample => {
            const div = document.createElement('div');
            div.className = 'sample-item';
            div.innerHTML = `
                <img src="${sample.image_data}" alt="Real sample">
                <div class="sample-label">ID: ${sample.video_id}</div>
            `;
            realGrid.appendChild(div);
        });
        
        document.getElementById('trainingSamplesModal').style.display = 'flex';
    } catch (error) {
        console.error('Error loading samples:', error);
        showCustomAlert('Loading Failed', 'Error loading training samples', 'warning');
    }
}

function closeTrainingSamples() {
    document.getElementById('trainingSamplesModal').style.display = 'none';
}

// Close modals when clicking outside
document.getElementById('featuresModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'featuresModal') {
        closeFeatures();
    }
});

document.getElementById('trainingSamplesModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'trainingSamplesModal') {
        closeTrainingSamples();
    }
});

// Custom Alert Modal
function showCustomAlert(title, message, type = 'info') {
    // Remove existing alert if any
    const existing = document.getElementById('customAlertModal');
    if (existing) existing.remove();
    
    // Create modal
    const modal = document.createElement('div');
    modal.id = 'customAlertModal';
    modal.className = 'custom-alert-modal';
    
    const icon = type === 'info' ? '💡' : (type === 'success' ? '✓' : '⚠️');
    const color = type === 'info' ? '#4ECDC4' : (type === 'success' ? '#00D9A5' : '#FF9800');
    
    modal.innerHTML = `
        <div class="custom-alert-content">
            <div class="custom-alert-icon" style="color: ${color};">
                ${icon}
            </div>
            <h3 class="custom-alert-title">${title}</h3>
            <p class="custom-alert-message">${message}</p>
            <button class="custom-alert-btn" onclick="closeCustomAlert()" style="background: ${color};">
                Got it!
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('show'), 10);
}

function closeCustomAlert() {
    const modal = document.getElementById('customAlertModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    }
}
