# Advanced Features Guide

## 🚀 Features Overview

### Model Training
- **Dataset**: 140,000 images from Kaggle (70k real + 70k fake)
- **Training subset**: 10,000 images (optimized for 1-hour training)
- **Architecture**: EfficientNetB0 with fine-tuned last 30 layers
- **Accuracy**: 70-90% on validation set
- **Detection**: Face-based deepfake detection using CNN

### Dataset Sources
- **Primary**: Kaggle "140k Real and Fake Faces" dataset
- **Training samples**: 5,000 real + 5,000 fake
- **Validation**: 1,000 real + 1,000 fake
- **Test**: 500 real + 500 fake
- **Optional**: FaceForensics++ dataset support (requires approval)

---

## 🎯 Core Features

### 1. **Temporal Analysis** 📊
Analyzes videos frame-by-frame to detect temporal inconsistencies in deepfakes.

**How it works:**
- Samples 2 frames per second from the video
- Detects and analyzes faces in each frame
- Plots prediction scores over time
- Calculates temporal variance (inconsistency indicator)
- Detects sudden prediction jumps

**What to look for:**
- **High variance**: Indicates inconsistent manipulation across frames
- **Sudden jumps**: Shows frames where manipulation quality changes
- **Consistency score**: Higher = more consistent (real videos tend to be more consistent)

**Use case:** Real videos show consistent face structure across frames. Deepfakes often have frame-to-frame inconsistencies due to varying synthesis quality.

---

### 2. **Attention Heatmap** 🔥
Visualizes which regions of the face are most suspicious.

**Features:**
- Highlights manipulated areas
- Shows confidence distribution across face regions
- Helps identify specific artifacts

**Use case:** Useful for understanding WHY the model classified an image as fake. Common suspicious areas include:
- Around the eyes and eyebrows
- Nose and mouth boundaries  
- Hairline and jaw edges

---

### 3. **Batch Processing** 📦
Process multiple files simultaneously for efficiency.

**Features:**
- Upload multiple images or videos at once
- Aggregated statistics (total fake vs real)
- Individual results for each file
- Summary table with all predictions

**Use case:** Perfect for:
- Analyzing entire folders of media
- Quick screening of multiple suspects
- Bulk content moderation

---

### 4. **Training Data Explorer** 🗂️
Browse actual samples from the Kaggle training dataset.

**What you can see:**
- **Fake samples**: AI-generated deepfake faces
- **Real samples**: Authentic human faces
- **Dataset info**: 140k total images used for training

**Educational value:**
- Understand what the model was trained on
- See real examples of deepfakes vs real faces
- Compare quality and characteristics of modern deepfakes

**Note**: The current web interface shows samples from the small demo dataset. The full Kaggle dataset contains professional-quality deepfakes.

---

### 5. **Adjustable Detection Threshold** ⚙️
Fine-tune the sensitivity of deepfake detection.

**How it works:**
- Default threshold: 0.50 (50%)
- Adjustable range: 0.10 - 0.90
- Real-time adjustment via web interface
- Instant effect on new predictions

**Use cases:**
- **Lower threshold (0.25-0.40)**: More sensitive, catches subtle fakes but may have false positives
- **Default (0.50)**: Balanced detection
- **Higher threshold (0.60-0.75)**: Conservative, only flags obvious fakes

**How to adjust:**
1. Click "Statistics" in web interface
2. Use the threshold slider
3. Click "Apply Threshold"
4. Test with new images

---

## 🗂️ Dataset Management

### Quick Training Setup
The project includes optimized scripts for fast model training:

**Files:**
- `setup_quick_training.py` - Creates 10k image subset
- `06-download_kaggle_dataset.py` - Downloads full Kaggle dataset
- `07-setup_kaggle_for_training.py` - Prepares dataset structure
- `04-download_faceforensics.py` - FaceForensics++ helper

**Training modes:**
- **Quick mode** (`--quick` flag): 30-45 minutes, 10k images, 70-90% accuracy
- **Full mode**: 6-8 hours, 100k images, 90-95% accuracy

**Command:**
```bash
python 03-train_cnn.py --quick  # Fast training
python 03-train_cnn.py          # Full training
```

---

## 📈 Understanding the Metrics

### Confidence Score
- **0-50%**: Likely REAL
- **50-75%**: Possibly FAKE  
### Confidence Score
- **0-50%**: Likely REAL (model outputs low scores for real faces)
- **50-75%**: Possibly FAKE (borderline detection)
- **75-100%**: Highly likely FAKE (strong deepfake indicators)

**Note**: The score represents how "fake" the model thinks the image is. Lower scores = more real.

### Detection Threshold
- **Default**: 0.50 (classify as FAKE if score ≥ 0.50)
- **Adjustable**: Can be lowered to catch subtle fakes or raised to reduce false positives
- **Current model**: May need threshold of 0.25-0.40 depending on training results
- **< 0.01**: Very consistent (typical for real videos)
- **0.01-0.05**: Some variation (could be real or high-quality fake)
- **> 0.05**: High inconsistency (likely fake with varying quality)

### Temporal Variance
- **< 0.01**: Very consistent (typical for real videos)
- **0.01-0.05**: Some variation (could be real or high-quality fake)
- **> 0.05**: High inconsistency (likely fake with varying quality)

### Consistency Score
- **90-100%**: Excellent consistency
- **70-90%**: Good consistency
- **< 70%**: Poor consistency (red flag for deepfakes)

---

## 🔬 Technical Details

### Detection Pipeline
1. **Face Detection**: MTCNN locates faces with bounding boxes
2. **Preprocessing**: Resize to 128x128, normalize pixel values to [0,1]
3. **Inference**: EfficientNetB0 CNN model with custom classifier
4. **Post-processing**: Threshold comparison, confidence calculation, visualization

### Model Architecture (Quick Mode)
- **Base**: EfficientNetB0 (pre-trained on ImageNet)
- **Fine-tuning**: Last 30 layers trainable
- **Custom layers**: Dense(128) → Dropout(0.5) → Dense(1, sigmoid)
- **Total parameters**: 4.2M (164K trainable)
- **Input size**: 128x128x3 RGB images
- **Output**: Single value [0-1] indicating "fakeness"

### Training Details (Quick Mode)
- **Training set**: 10,000 images (5k real + 5k fake)
- **Validation set**: 2,000 images (1k real + 1k fake)  
- **Test set**: 1,000 images (500 real + 500 fake)
- **Batch size**: 64
- **Epochs**: 15 (with early stopping, patience=3)
- **Optimizer**: Adam (lr=0.0001)
- **Loss**: Binary crossentropy
- **Training time**: 30-45 minutes on CPU
- **Expected accuracy**: 70-90%

### Training Details (Full Mode)
- **Training set**: 100,000 images (50k real + 50k fake)
- **Validation set**: 20,000 images (10k real + 10k fake)
- **Test set**: 20,000 images (10k real + 10k fake)
- **Training time**: 6-8 hours on CPU
- **Expected accuracy**: 90-95%

---

## 📊 Dataset Statistics

### Demo Dataset (Original)
| Metric | Value |
|--------|-------|
| Total Videos | 5 |
| Fake Videos | 4 |
| Real Videos | 1 |
| Total Extracted Faces | 61 |
| Training Samples | 25 |
| Validation Samples | 3 |
| Test Samples | 6 |

### Kaggle Dataset (Current)
| Metric | Quick Mode | Full Mode |
|--------|-----------|-----------|
| Total Images | 13,000 | 140,000 |
| Training | 10,000 | 100,000 |
| Validation | 2,000 | 20,000 |
| Test | 1,000 | 20,000 |
| Real/Fake Split | 50/50 | 50/50 |
| Image Quality | Professional | Professional |
| Training Time | 30-45 min | 6-8 hours |
| Expected Accuracy | 70-90% | 90-95% |

---

## 💡 Best Practices

### For Single Image Analysis
1. Upload clear, well-lit images with visible faces
2. Ensure faces are not obscured or heavily filtered
3. Check the attention heatmap for suspicious regions
4. Review confidence score and adjust threshold if needed
5. Test with multiple images for better confidence

### For Video Analysis
1. Use temporal analysis for frame-by-frame insights
2. Check for prediction jumps (indicates inconsistent manipulation)
3. Compare consistency score with overall confidence
4. Higher frame count = more reliable statistical analysis
5. Look for artifacts in specific frames

### For Batch Processing
1. Group similar content types (all images or all videos)
2. Review summary statistics before diving into details
3. Investigate high-confidence detections manually
4. Use for initial screening, then verify suspicious files
5. Export results for documentation

### For Threshold Adjustment
1. **Default (0.50)**: Start here for balanced detection
2. **Lower (0.25-0.40)**: Use when you need high sensitivity (security applications)
3. **Higher (0.60-0.75)**: Use when false positives are costly (journalism verification)
4. Test threshold with known fake and real samples
5. Document your threshold choice for consistency

---

## 🎯 Future Enhancements

### Potential New Features:
1. **Export Reports**: Generate PDF reports with analysis results and visualizations
2. **Model Ensemble**: Combine predictions from multiple architectures (ResNet, Xception, etc.)
3. **3D Face Analysis**: Detect depth and geometry inconsistencies
4. **Audio-Visual Sync**: Check for lip-sync and voice manipulation issues
5. **Real-time Webcam Detection**: Live deepfake detection from camera feed
6. **API Access**: RESTful API for integration with other systems
7. **Advanced Metrics**: PSNR, SSIM, and other quality metrics
8. **User Feedback Loop**: Allow users to report false positives/negatives for retraining

### Dataset Expansion Options:
1. **FaceForensics++**: Request access for 1000+ high-quality samples
2. **Celeb-DF**: 5,639 celebrity deepfake videos
3. **DFDC**: Meta's 124k+ video dataset
4. **Custom Dataset**: Train on domain-specific data (e.g., company employees)

---

## 🛠️ API Endpoints

### Core Detection
```
POST /upload
Content-Type: multipart/form-data
Body: file (image or video)
Response: {
  overall_prediction: "FAKE" | "REAL",
  overall_confidence: 0-100,
  faces_detected: number,
  face_results: [{face_number, prediction, confidence, score}],
  processed_image: base64
}
```

### Batch Processing
```
POST /batch-upload
Content-Type: multipart/form-data
Body: files[] (multiple images/videos)
Response: {
  results: [{filename, prediction, confidence, ...}],
  total_processed: number,
  summary: {fake_count, real_count}
}
```

### Temporal Analysis
```
POST /temporal-analysis
Content-Type: multipart/form-data
Body: file (video)
Response: {
  overall_prediction: "FAKE" | "REAL",
  frame_predictions: [{frame_number, timestamp, prediction, confidence}],
  temporal_variance: number,
  consistency_score: number,
  chart_data: {...}
}
```

### Attention Heatmap
```
POST /heatmap
Content-Type: multipart/form-data
Body: file (image)
Response: {
  heatmap_image: base64,
  suspicious_regions: [{x, y, width, height, confidence}]
}
```

### Threshold Management
```
POST /set-threshold
Content-Type: application/json
Body: {threshold: 0.0-1.0}
Response: {
  message: "Threshold updated",
  threshold: number
}

GET /stats
Response: {
  dataset_stats: {...},
  model_info: {...},
  current_threshold: number
}
```

### Training Samples
```
GET /training-samples
Response: {
  samples: [{filename, label, source, faces: [...]}],
  metadata: {...}
}
```

---

## 📚 Additional Resources

### Scripts Reference
- `00-convert_video_to_image.py` - Extract frames from videos
- `01a-crop_faces_with_mtcnn.py` - Face detection with MTCNN
- `01b-crop_faces_with_azure-vision-api.py` - Face detection with Azure (optional)
- `02-prepare_fake_real_dataset.py` - Organize and split dataset
- `03-train_cnn.py` - Train the CNN model (supports --quick flag)
- `04-download_faceforensics.py` - Download FaceForensics++ dataset
- `05-integrate_dataset.py` - Integrate downloaded datasets
- `06-download_kaggle_dataset.py` - Download Kaggle dataset automatically
- `07-setup_kaggle_for_training.py` - Prepare Kaggle dataset structure
- `setup_quick_training.py` - Create optimized 10k subset for fast training
- `retrain_model.py` - Automated retraining with improvements
- `monitor_training.py` - Real-time training progress monitor
- `check_status.py` - Quick training status checker
- `app.py` - Flask web application

### Documentation Files
- `README.md` - Project overview and setup
- `FEATURES_GUIDE.md` - This file - comprehensive feature documentation
- `WEB_UI_README.md` - Web interface user guide
- `ACCURACY_IMPROVEMENTS.md` - Tips for improving model accuracy
- `SOLUTION.md` - Quick fixes for common detection issues

---

## 🔐 Security & Privacy

### Data Handling
- All processing done locally on your machine
- No data sent to external servers (except Azure Vision API if enabled)
- Uploaded files processed in memory when possible
- Temporary files cleaned automatically

### Model Security
- Model weights stored locally
- No telemetry or usage tracking
- Open source code for transparency
- Can be deployed in air-gapped environments

---

## 🤝 Contributing

Want to improve the detection system? Here are areas to contribute:

1. **Dataset expansion**: Add more diverse training samples
2. **Model improvements**: Try different architectures (ResNet, Xception, Vision Transformer)
3. **Feature engineering**: Extract additional facial features
4. **Performance optimization**: Speed up inference with quantization/pruning
5. **UI enhancements**: Improve web interface design and usability

---

**Last Updated**: November 27, 2025  
**Model Version**: Quick Training v1.0 (Kaggle Dataset)  
**Training Dataset**: 10,000 images (5k real + 5k fake)
Response: {frame_predictions, temporal_variance, consistency_score, ...}
```

### Heatmap Generation
```
POST /heatmap
Body: file (image, multipart/form-data)
Response: {heatmap_image, prediction, suspicious_score}
```

### Training Samples
```
GET /training-samples
Response: {fake_samples: [...], real_samples: [...]}
```

### Statistics
```
GET /stats
Response: {model_loaded, dataset_info: {...}}
```

---

## 🎓 Educational Use

This tool is perfect for:
- **Research**: Understanding deepfake detection techniques
- **Education**: Teaching ML and computer vision concepts
- **Forensics**: Analyzing suspected manipulated media
- **Content Moderation**: Screening user-generated content
- **Journalism**: Fact-checking visual evidence

---

## ⚠️ Limitations

- **Dataset size**: Small training set (25 samples) may limit generalization
- **Face detection dependency**: Requires clear, visible faces
- **Video processing**: Limited to 30 frames for speed
- **Lighting/quality**: Works best with good quality images
- **Specific to face swaps**: Trained on face-swap deepfakes only

---

## 📝 Tips for Better Results

1. **Image Quality**: Use high-resolution images when possible
2. **Face Visibility**: Ensure faces are front-facing and unobstructed
3. **Lighting**: Good lighting helps detection accuracy
4. **Video Length**: Longer videos provide more data points for temporal analysis
5. **Multiple Angles**: Analyze multiple frames/angles when available
