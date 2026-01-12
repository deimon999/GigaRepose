# 🔍 DeepFake Detection System

<p align="center">
  <img src="img/dfdetect-home.png" alt="DeepFake Detect" width="80%">
</p>

A comprehensive deep learning-based deepfake detection system built with Python, TensorFlow/Keras, and Flask. This project provides both a training pipeline for building deepfake detection models and a web-based interface for real-time analysis of images and videos.

## ✨ Features

- **🤖 Deep Learning Model**: EfficientNet-based binary classifier for detecting manipulated media
- **🌐 Web Interface**: Flask-based web application for easy deepfake analysis
- **📹 Video Analysis**: Frame-by-frame analysis with face detection using MTCNN
- **🖼️ Image Analysis**: Single image deepfake detection with confidence scores
- **📊 Batch Processing**: Analyze multiple files at once
- **📧 Contact System**: Built-in contact form with email notifications
- **🔄 Training Pipeline**: Complete workflow from data preparation to model training

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **Deep Learning**: TensorFlow, Keras, EfficientNet
- **Face Detection**: MTCNN (Multi-task Cascaded Convolutional Networks)
- **Image Processing**: OpenCV, Pillow
- **Frontend**: HTML, CSS, JavaScript

## 📋 Prerequisites

- Python 3.7+
- CUDA-compatible GPU (recommended for training)
- 8GB+ RAM

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/deimon999/GigaRepose.git
   cd GigaRepose
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📁 Project Structure

```
GigaRepose/
├── app.py                          # Flask web application
├── requirements.txt                # Python dependencies
├── 00-convert_video_to_image.py    # Video frame extraction
├── 01a-crop_faces_with_mtcnn.py    # Face detection with MTCNN
├── 01b-crop_faces_with_azure-vision-api.py  # Face detection with Azure API
├── 02-prepare_fake_real_dataset.py # Dataset balancing and splitting
├── 03-train_cnn.py                 # Model training script
├── 04-download_faceforensics.py    # FaceForensics++ downloader
├── 05-integrate_dataset.py         # Dataset integration
├── 06-download_kaggle_dataset.py   # Kaggle dataset downloader
├── 07-setup_kaggle_for_training.py # Kaggle training setup
├── train_enhanced.py               # Enhanced training script
├── train_efficientnet.py           # EfficientNet training
├── static/                         # CSS, JavaScript files
├── templates/                      # HTML templates
└── FaceForensics/                  # FaceForensics++ tools
```

## 🎯 Usage

### Running the Web Application

```bash
python app.py
```

Then open your browser and navigate to `http://localhost:5000`

### Training Pipeline

#### Step 0: Convert Videos to Images
```bash
python 00-convert_video_to_image.py
```
Extracts frames from videos with intelligent resizing based on video resolution.

#### Step 1: Extract Faces
```bash
python 01a-crop_faces_with_mtcnn.py
```
Detects and crops faces from images using MTCNN with 30% margin padding.

#### Step 2: Prepare Dataset
```bash
python 02-prepare_fake_real_dataset.py
```
Balances fake/real samples and splits into train/validation/test sets (80:10:10).

#### Step 3: Train Model
```bash
python 03-train_cnn.py
```
Trains the EfficientNet-based classifier on the prepared dataset.

### Alternative Training Scripts

- `train_enhanced.py` - Enhanced training with additional callbacks
- `train_efficientnet.py` - Direct EfficientNet training
- `train_robust.py` - Robust training with data augmentation
- `train_full_dataset.py` - Training on complete dataset

## 📊 Supported Datasets

The model can be trained on various deepfake datasets:

- [DeepFake-TIMIT](https://www.idiap.ch/dataset/deepfaketimit)
- [FaceForensics++](https://github.com/ondyari/FaceForensics)
- [Google Deep Fake Detection (DFD)](https://ai.googleblog.com/2019/09/contributing-data-to-deepfake-detection.html)
- [Celeb-DF](https://github.com/danmohaha/celeb-deepfakeforensics)
- [Facebook DFDC](https://ai.facebook.com/datasets/dfdc/)
- [Kaggle Deepfake Detection Challenge](https://www.kaggle.com/c/deepfake-detection-challenge)

## 🧠 Model Architecture

The detection model uses **EfficientNet B0** as the backbone with custom modifications:

- Input layer: 128x128x3 RGB images
- Global Max Pooling layer
- 2 Fully Connected layers with ReLU activation
- Output layer with Sigmoid activation (binary classification)
- Output: Probability score (0 = Fake, 1 = Real)

## 📸 Supported File Formats

**Images**: PNG, JPG, JPEG, BMP, WebP, AVIF

**Videos**: MP4, AVI, MOV, MKV, FLV, WMV, MPG, MPEG, M4V, 3GP, WebM, OGV

## 🌐 Web Interface Features

- **Home Page**: Project overview and information
- **Analyzer**: Upload and analyze images/videos
  - Drag & drop file upload
  - Real-time analysis results
  - Confidence scores with visual indicators
  - Batch file processing
- **Contact Form**: Send messages with email notifications

## ⚙️ Configuration

Key configuration options in `app.py`:

```python
DETECTION_THRESHOLD = 0.5      # Classification threshold
UNCERTAINTY_RANGE = 0.25       # Uncertainty zone around threshold
MAX_CONTENT_LENGTH = 200 MB    # Maximum upload size
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [EfficientNet](https://github.com/qubvel/efficientnet) for the backbone architecture
- [MTCNN](https://github.com/ipazc/mtcnn) for face detection
- [FaceForensics++](https://github.com/ondyari/FaceForensics) for dataset tools
- Original work by [Aaron Chong](https://github.com/aaronchong888) and [Hugo Ng](https://github.com/hugoclong)

## 📧 Contact

For questions or feedback, use the contact form in the web application or open an issue on GitHub.

---

<p align="center">
  Made with ❤️ for fighting misinformation
</p>
