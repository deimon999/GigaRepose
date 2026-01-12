# DeepFake Detection Studio - Web UI

A modern web interface for detecting deepfake images and videos using the trained CNN model.

## Features

- 🎨 Modern, dark-themed UI inspired by professional editing software
- 📤 Drag-and-drop file upload
- 🖼️ Support for images (JPG, PNG) and videos (MP4, AVI, MOV)
- 🎯 Real-time deepfake detection with confidence scores
- 👤 Multiple face detection and individual analysis
- 📊 Visual results with processed image display
- 📈 Dataset statistics viewer
- ⚡ Fast inference using the trained EfficientNetB0 model

## Installation

1. Install the required dependencies:
```bash
pip install flask pillow
```

2. Make sure you have the trained model at `./tmp_checkpoint/best_model.h5`

## Running the Application

Start the Flask server:
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Usage

1. **Upload Media**: 
   - Drag and drop an image or video file
   - Or click "Browse Files" to select a file
   - Supported formats: JPG, PNG, MP4, AVI, MOV

2. **Analyze**: 
   - Click "Analyze for Deepfakes" button
   - Wait for the analysis to complete
   - View the results with confidence scores

3. **View Results**:
   - Overall verdict (REAL or FAKE)
   - Confidence percentage
   - Number of faces detected
   - Individual face analysis (for images)
   - Processed image with face bounding boxes

4. **Statistics**:
   - Click the "Statistics" button in the header
   - View dataset information and model status

## How It Works

### Image Processing
1. Detects faces using MTCNN
2. Extracts and preprocesses each face region
3. Runs inference using the trained model
4. Displays results with bounding boxes and labels

### Video Processing
1. Samples frames from the video (1 frame per second)
2. Detects faces in each sampled frame
3. Analyzes up to 10 frames for efficiency
4. Aggregates predictions for overall verdict

## Technical Details

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript
- **Deep Learning**: TensorFlow/Keras with EfficientNetB0
- **Face Detection**: MTCNN
- **Image Processing**: OpenCV, Pillow

## API Endpoints

- `GET /` - Main web interface
- `POST /upload` - Upload and analyze media file
- `GET /stats` - Get dataset statistics

## Customization

### Modify Detection Parameters

Edit `app.py` to adjust:
- `MAX_CONTENT_LENGTH`: Maximum file upload size (default: 16MB)
- Frame sampling rate for videos
- Number of frames to analyze
- Model input size (currently 128x128)

### UI Styling

Modify `static/css/style.css` to customize:
- Color scheme (defined in `:root` CSS variables)
- Layout and spacing
- Animation effects

## Troubleshooting

**Model not loading:**
- Ensure `best_model.h5` exists in `./tmp_checkpoint/`
- Check that the model was trained successfully

**MTCNN errors:**
- The first run may be slow as MTCNN loads
- Ensure sufficient memory is available

**File upload fails:**
- Check file size (max 16MB by default)
- Verify file format is supported
- Check server logs for detailed errors

## Performance Tips

- For faster processing, use images instead of videos
- Videos are sampled at 1 fps to balance speed and accuracy
- Use a GPU for faster inference (if available)
- Close other applications to free up memory

## Screenshot

The UI features:
- Dark, modern theme
- Intuitive drag-and-drop interface
- Real-time analysis feedback
- Professional result presentation
- Detailed face-by-face breakdown
