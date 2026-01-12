from flask import Flask, render_template, request, jsonify
import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from mtcnn import MTCNN
import base64
from io import BytesIO
from PIL import Image
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max payload to allow multi-video uploads

# Detection threshold (adjustable for sensitivity)
# Since current model has low accuracy, using a conservative approach
# Model outputs: 0 = FAKE, 1 = REAL (alphabetical folder order: fake, real)
# Wider uncertainty zone because model is untrained (50% accuracy)
DETECTION_THRESHOLD = 0.5
UNCERTAINTY_RANGE = 0.25  # ±0.25 around threshold = uncertain zone (0.25 to 0.75)

ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.avif'}
ALLOWED_VIDEO_EXTENSIONS = {
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpg', '.mpeg', '.m4v', '.3gp', '.webm', '.ogv'
}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load the trained model
MODEL_PATH = './tmp_checkpoint/final_model.h5'
model = None
detector = None

def load_detection_model():
    global model, detector
    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        detector = MTCNN()
        print("Model loaded successfully!")
    else:
        print(f"Model not found at {MODEL_PATH}")


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename.lower())[1]


def is_allowed_image(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_IMAGE_EXTENSIONS


def is_allowed_video(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_VIDEO_EXTENSIONS


@app.errorhandler(413)
def request_entity_too_large(_error):
    return jsonify({
        'error': 'Uploaded files are too large. Please keep the total payload under 200MB.'
    }), 413

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/analyzer')
def analyzer():
    return render_template('analyzer.html')

@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    
    # Save contact messages to a JSON file
    contact_file = 'contact_messages.json'
    messages = []
    
    # Load existing messages if file exists
    if os.path.exists(contact_file):
        try:
            with open(contact_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except:
            messages = []
    
    # Add new message with timestamp
    new_message = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'name': data.get('name', 'Anonymous'),
        'email': data.get('email', 'No email provided'),
        'subject': data.get('subject', 'No subject'),
        'message': data.get('message', 'No message')
    }
    messages.append(new_message)
    
    # Save to file
    try:
        with open(contact_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        
        # Send email notification
        send_contact_email(new_message)
        
        print(f"Contact form received from {new_message['name']} ({new_message['email']})")
        return jsonify({'success': True, 'message': 'Thank you! Your message has been received.'})
    except Exception as e:
        print(f"Error saving contact message: {e}")
        return jsonify({'success': False, 'message': 'Failed to save message'}), 500

def send_contact_email(message_data):
    """Send email notification when contact form is submitted"""
    try:
        # Email configuration
        RECIPIENT_EMAIL = "kyndiahdeimon753@gmail.com"
        SENDER_EMAIL = "kyndiahdeimon753@gmail.com"  # Must match the Gmail account for SMTP login
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"DeepFake Detector Contact: {message_data['subject']}"
        msg['From'] = f"DeepFake Detector <{SENDER_EMAIL}>"
        msg['To'] = RECIPIENT_EMAIL
        msg['Reply-To'] = message_data['email']
        
        # HTML email body
        html = f"""
        <html>
          <head></head>
          <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
              <h2 style="color: #4ecdc4; border-bottom: 3px solid #4ecdc4; padding-bottom: 10px;">New Contact Form Submission</h2>
              
              <div style="margin: 20px 0;">
                <p style="margin: 10px 0;"><strong style="color: #555;">From:</strong> {message_data['name']}</p>
                <p style="margin: 10px 0;"><strong style="color: #555;">Email:</strong> <a href="mailto:{message_data['email']}">{message_data['email']}</a></p>
                <p style="margin: 10px 0;"><strong style="color: #555;">Subject:</strong> {message_data['subject']}</p>
                <p style="margin: 10px 0;"><strong style="color: #555;">Date:</strong> {message_data['timestamp']}</p>
              </div>
              
              <div style="background-color: #f9f9f9; padding: 20px; border-left: 4px solid #4ecdc4; margin: 20px 0;">
                <p style="margin: 0; color: #333; white-space: pre-wrap;">{message_data['message']}</p>
              </div>
              
              <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
              
              <p style="color: #888; font-size: 12px; margin: 10px 0;">
                This message was sent from the DeepFake Detection Studio contact form.
              </p>
              <p style="color: #888; font-size: 12px; margin: 10px 0;">
                Reply directly to this email to respond to {message_data['name']}.
              </p>
            </div>
          </body>
        </html>
        """
        
        # Plain text alternative
        text = f"""
New Contact Form Submission

From: {message_data['name']}
Email: {message_data['email']}
Subject: {message_data['subject']}
Date: {message_data['timestamp']}

Message:
{message_data['message']}

---
This message was sent from the DeepFake Detection Studio contact form.
Reply to {message_data['email']} to respond.
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send via Gmail SMTP
        # Note: You need to set up an App Password in your Google Account
        # Go to: https://myaccount.google.com/apppasswords
        # Generate an app password for "Mail" and use it here
        
        # Send email via Gmail SMTP
        GMAIL_APP_PASSWORD = "ysgcqfvoaoxjimuv"
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {RECIPIENT_EMAIL}")
        
        # Also log to file for backup
        email_log = 'email_notifications.txt'
        with open(email_log, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Email sent to: {RECIPIENT_EMAIL}\n")
            f.write(f"From: {message_data['name']} ({message_data['email']})\n")
            f.write(f"Subject: {message_data['subject']}\n")
            f.write(f"Time: {message_data['timestamp']}\n")
            f.write(f"Message: {message_data['message']}\n")
        
    except Exception as e:
        error_log = 'email_errors.txt'
        with open(error_log, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"ERROR at {datetime.now()}\n")
            f.write(f"Error type: {type(e).__name__}\n")
            f.write(f"Error message: {str(e)}\n")
            f.write(f"Recipient: {message_data.get('email', 'unknown')}\n")
        print(f"Error sending email: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail the request if email fails

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        # Save uploaded file
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Process image or video
        if is_allowed_image(filename):
            result = process_image(filename)
        elif is_allowed_video(filename):
            result = process_video(filename)
        else:
            return jsonify({
                'error': 'Unsupported file format. Allowed images: PNG, JPG, JPEG, BMP, WEBP, AVIF. '
                         'Allowed videos: MP4, AVI, MOV, MKV, FLV, WMV, MPG, MPEG, M4V, 3GP, WEBM, OGV.'
            }), 400
        
        # Clean up
        os.remove(filename)
        
        return jsonify(result)

def process_image(image_path):
    """Process a single image and detect if it's a deepfake"""
    if model is None or detector is None:
        return {'error': 'Model not loaded'}
    
    # Read image
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    faces = detector.detect_faces(img_rgb)
    
    if len(faces) == 0:
        return {
            'prediction': 'No face detected',
            'confidence': 0,
            'faces_detected': 0
        }
    
    results = []
    for idx, face_data in enumerate(faces):
        # Extract face region
        x, y, width, height = face_data['box']
        x, y = max(0, x), max(0, y)
        
        # Add margin
        margin = 20
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(img_rgb.shape[1], x + width + margin)
        y2 = min(img_rgb.shape[0], y + height + margin)
        
        face_img = img_rgb[y1:y2, x1:x2]
        
        # Preprocess for model (model expects 64x64 input)
        face_resized = cv2.resize(face_img, (64, 64))
        face_array = face_resized / 255.0
        face_array = np.expand_dims(face_array, axis=0)
        
        # Predict
        prediction = model.predict(face_array, verbose=0)[0][0]
        
        # Log prediction for debugging
        print(f"Face {idx + 1}: Raw score = {prediction:.4f}, Threshold = {DETECTION_THRESHOLD:.4f}")
        
        # IMPORTANT: Label mapping is alphabetical - fake=0, real=1
        # Higher score (closer to 1) = REAL, lower score (closer to 0) = FAKE
        
        # Check if prediction is in uncertain zone
        lower_uncertain = DETECTION_THRESHOLD - UNCERTAINTY_RANGE  # 0.35
        upper_uncertain = DETECTION_THRESHOLD + UNCERTAINTY_RANGE  # 0.65
        
        if lower_uncertain <= prediction <= upper_uncertain:
            # UNCERTAIN - model can't tell
            is_fake = None
            distance_from_center = abs(prediction - DETECTION_THRESHOLD)
            confidence = 50.0 + (distance_from_center / UNCERTAINTY_RANGE * 50.0)
            label = f"UNCERTAIN: {min(confidence, 99.9):.1f}%"
            color = (255, 165, 0)  # Orange (BGR format)
        elif prediction < lower_uncertain:
            # Strongly FAKE
            is_fake = True
            if lower_uncertain > 0:
                confidence = min(((lower_uncertain - prediction) / lower_uncertain) * 100, 100.0)
            else:
                confidence = 100.0
            label = f"FAKE: {confidence:.1f}%"
            color = (0, 0, 255)  # Red (BGR format)
        else:
            # Strongly REAL
            is_fake = False
            denominator = 1.0 - upper_uncertain
            if denominator > 0:
                confidence = min(((prediction - upper_uncertain) / denominator) * 100, 100.0)
            else:
                confidence = 100.0
            label = f"REAL: {confidence:.1f}%"
            color = (0, 255, 0)  # Green (BGR format)
        
        # Draw rectangle on original image
        cv2.rectangle(img, (x, y), (x + width, y + height), color, 2)
        cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        
        results.append({
            'face_number': idx + 1,
            'prediction': 'FAKE' if is_fake is True else ('REAL' if is_fake is False else 'UNCERTAIN'),
            'confidence': float(confidence),
            'score': float(prediction)
        })
    
    # Convert processed image to base64
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Calculate overall verdict
    fake_count = sum(1 for r in results if r['prediction'] == 'FAKE')
    real_count = sum(1 for r in results if r['prediction'] == 'REAL')
    uncertain_count = sum(1 for r in results if r['prediction'] == 'UNCERTAIN')
    
    if uncertain_count > len(results) / 2:
        overall_prediction = 'UNCERTAIN'
    elif fake_count > real_count:
        overall_prediction = 'FAKE'
    else:
        overall_prediction = 'REAL'
    
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    
    return {
        'overall_prediction': overall_prediction,
        'overall_confidence': float(avg_confidence),
        'faces_detected': len(faces),
        'face_results': results,
        'processed_image': img_base64
    }

def generate_attention_heatmap(image_path):
    """Generate a heatmap showing which regions are most suspicious"""
    if model is None or detector is None:
        return {'error': 'Model not loaded'}
    
    img = cv2.imread(image_path)
    if img is None:
        return {'error': 'Failed to load image'}
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(img_rgb)
    
    if len(faces) == 0:
        return {'error': 'No face detected'}
    
    # Use first detected face
    x, y, width, height = faces[0]['box']
    margin = 20
    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(img_rgb.shape[1], x + width + margin)
    y2 = min(img_rgb.shape[0], y + height + margin)
    
    face_img = img_rgb[y1:y2, x1:x2]
    face_resized = cv2.resize(face_img, (64, 64))
    face_array = face_resized / 255.0
    face_array = np.expand_dims(face_array, axis=0)
    
    # Get prediction
    prediction = model.predict(face_array, verbose=0)[0][0]
    
    # Determine prediction category
    lower_uncertain = DETECTION_THRESHOLD - UNCERTAINTY_RANGE
    upper_uncertain = DETECTION_THRESHOLD + UNCERTAINTY_RANGE
    
    if lower_uncertain <= prediction <= upper_uncertain:
        pred_label = 'UNCERTAIN'
        confidence = 50.0 + (abs(prediction - DETECTION_THRESHOLD) / UNCERTAINTY_RANGE * 50.0)
    elif prediction < lower_uncertain:
        pred_label = 'FAKE'
        confidence = min(((lower_uncertain - prediction) / lower_uncertain) * 100, 100.0) if lower_uncertain > 0 else 100.0
    else:
        pred_label = 'REAL'
        denominator = 1.0 - upper_uncertain
        confidence = min(((prediction - upper_uncertain) / denominator) * 100, 100.0) if denominator > 0 else 100.0
    
    # Create heatmap overlay - scale intensity by how far from uncertain zone
    face_for_heatmap = cv2.resize((face_resized * 255).astype(np.uint8), (width, height))
    heatmap = cv2.applyColorMap(face_for_heatmap, cv2.COLORMAP_JET)
    
    # Ensure coordinates are valid
    y_end = min(y + height, img.shape[0])
    x_end = min(x + width, img.shape[1])
    heatmap = cv2.resize(heatmap, (x_end - x, y_end - y))
    
    overlay = cv2.addWeighted(img[y:y_end, x:x_end], 0.6, heatmap, 0.4, 0)
    img[y:y_end, x:x_end] = overlay
    
    # Draw bounding box
    color = (0, 255, 0) if pred_label == 'REAL' else ((255, 165, 0) if pred_label == 'UNCERTAIN' else (0, 0, 255))
    cv2.rectangle(img, (x, y), (x_end, y_end), color, 2)
    cv2.putText(img, f"{pred_label}: {confidence:.1f}%", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        'heatmap_image': img_base64,
        'prediction': pred_label,
        'confidence': float(confidence),
        'raw_score': float(prediction)
    }

def analyze_temporal_consistency(video_path):
    """Analyze video frame by frame to detect temporal inconsistencies"""
    if model is None or detector is None:
        return {'error': 'Model not loaded'}
    
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    frame_predictions = []
    frame_numbers = []
    frame_count = 0
    max_frames = 30  # Analyze up to 30 frames
    
    frame_interval = max(1, int(frame_rate / 2))  # Sample 2 frames per second
    
    while cap.isOpened() and len(frame_predictions) < max_frames:
        frame_id = cap.get(cv2.CAP_PROP_POS_FRAMES)
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if frame_id % frame_interval == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = detector.detect_faces(frame_rgb)
            
            if len(faces) > 0:
                face_data = faces[0]
                x, y, width, height = face_data['box']
                
                margin = 20
                x1 = max(0, x - margin)
                y1 = max(0, y - margin)
                x2 = min(frame_rgb.shape[1], x + width + margin)
                y2 = min(frame_rgb.shape[0], y + height + margin)
                
                face_img = frame_rgb[y1:y2, x1:x2]
                face_resized = cv2.resize(face_img, (64, 64))
                face_array = face_resized / 255.0
                face_array = np.expand_dims(face_array, axis=0)
                
                prediction = model.predict(face_array, verbose=0)[0][0]
                frame_predictions.append(float(prediction))
                frame_numbers.append(int(frame_id))
    
    cap.release()
    
    if len(frame_predictions) == 0:
        return {'error': 'No faces detected in video'}
    
    # Calculate temporal variance (inconsistency indicator)
    variance = float(np.var(frame_predictions))
    avg_prediction = float(np.mean(frame_predictions))
    
    # Detect sudden jumps
    jumps = []
    for i in range(1, len(frame_predictions)):
        diff = abs(frame_predictions[i] - frame_predictions[i-1])
        if diff > 0.3:  # Significant change
            jumps.append({
                'frame': frame_numbers[i],
                'change': float(diff)
            })
    
    return {
        'frame_predictions': frame_predictions,
        'frame_numbers': frame_numbers,
        'average_prediction': avg_prediction,
        'temporal_variance': variance,
        'inconsistency_jumps': jumps,
        'overall_prediction': 'FAKE' if avg_prediction > DETECTION_THRESHOLD else 'REAL',
        'consistency_score': float(100 - (variance * 100)),  # Lower variance = more consistent
        'total_frames_analyzed': len(frame_predictions)
    }

def process_video(video_path):
    """Process video and analyze frames"""
    if model is None or detector is None:
        return {'error': 'Model not loaded'}
    
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Sample every second
    frame_interval = max(1, int(frame_rate))
    predictions = []
    frame_count = 0
    first_frame_with_face = None
    first_face_box = None
    
    while cap.isOpened() and frame_count < 10:  # Analyze max 10 frames
        frame_id = cap.get(cv2.CAP_PROP_POS_FRAMES)
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if frame_id % frame_interval == 0:
            # Detect faces in frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = detector.detect_faces(frame_rgb)
            
            if len(faces) > 0:
                face_data = faces[0]  # Use first detected face
                x, y, width, height = face_data['box']
                
                # Save first frame with face for preview
                if first_frame_with_face is None:
                    first_frame_with_face = frame.copy()
                    first_face_box = (x, y, width, height)
                
                margin = 20
                x1 = max(0, x - margin)
                y1 = max(0, y - margin)
                x2 = min(frame_rgb.shape[1], x + width + margin)
                y2 = min(frame_rgb.shape[0], y + height + margin)
                
                face_img = frame_rgb[y1:y2, x1:x2]
                face_resized = cv2.resize(face_img, (64, 64))
                face_array = face_resized / 255.0
                face_array = np.expand_dims(face_array, axis=0)
                
                prediction = model.predict(face_array, verbose=0)[0][0]
                predictions.append(prediction)
            
            frame_count += 1
    
    cap.release()
    
    if len(predictions) == 0:
        return {
            'overall_prediction': 'No faces detected',
            'overall_confidence': 0,
            'frames_analyzed': frame_count
        }
    
    # Calculate average prediction using 3-zone detection
    avg_prediction = np.mean(predictions)
    
    # Apply 3-zone detection logic
    lower_uncertain = DETECTION_THRESHOLD - UNCERTAINTY_RANGE  # 0.35
    upper_uncertain = DETECTION_THRESHOLD + UNCERTAINTY_RANGE  # 0.65
    
    if lower_uncertain <= avg_prediction <= upper_uncertain:
        # UNCERTAIN zone
        overall_prediction = 'UNCERTAIN'
        distance_from_center = abs(avg_prediction - DETECTION_THRESHOLD)
        confidence = 50.0 + (distance_from_center / UNCERTAINTY_RANGE * 50.0)
    elif avg_prediction < lower_uncertain:
        # Strongly FAKE
        overall_prediction = 'FAKE'
        if lower_uncertain > 0:
            confidence = min(((lower_uncertain - avg_prediction) / lower_uncertain) * 100, 100.0)
        else:
            confidence = 100.0
    else:
        # Strongly REAL
        overall_prediction = 'REAL'
        denominator = 1.0 - upper_uncertain
        if denominator > 0:
            confidence = min(((avg_prediction - upper_uncertain) / denominator) * 100, 100.0)
        else:
            confidence = 100.0
    
    # Generate processed image with bounding box
    processed_image = None
    if first_frame_with_face is not None and first_face_box is not None:
        x, y, width, height = first_face_box
        
        # Determine color based on overall prediction
        if overall_prediction == 'FAKE':
            color = (0, 0, 255)  # Red
            label = f"FAKE: {confidence:.1f}%"
        elif overall_prediction == 'UNCERTAIN':
            color = (255, 165, 0)  # Orange
            label = f"UNCERTAIN: {confidence:.1f}%"
        else:
            color = (0, 255, 0)  # Green
            label = f"REAL: {confidence:.1f}%"
        
        cv2.rectangle(first_frame_with_face, (x, y), (x + width, y + height), color, 2)
        cv2.putText(first_frame_with_face, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', first_frame_with_face)
        processed_image = base64.b64encode(buffer).decode('utf-8')
    
    # Count frames by category
    fake_frames = sum(1 for p in predictions if p < lower_uncertain)
    uncertain_frames = sum(1 for p in predictions if lower_uncertain <= p <= upper_uncertain)
    real_frames = sum(1 for p in predictions if p > upper_uncertain)
    
    return {
        'overall_prediction': overall_prediction,
        'overall_confidence': float(confidence),
        'frames_analyzed': len(predictions),
        'prediction_score': float(avg_prediction),
        'fake_frames': fake_frames,
        'uncertain_frames': uncertain_frames,
        'real_frames': real_frames,
        'processed_image': processed_image
    }

@app.route('/batch-upload', methods=['POST'])
def batch_upload():
    """Process multiple files at once"""
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    results = []
    
    for file in files:
        if file.filename == '':
            continue
        
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        try:
            if is_allowed_image(filename):
                result = process_image(filename)
            elif is_allowed_video(filename):
                result = process_video(filename)
            else:
                results.append({
                    'filename': file.filename,
                    'error': 'Unsupported file format'
                })
                continue

            result['filename'] = file.filename
            results.append(result)
        except Exception as e:
            results.append({'filename': file.filename, 'error': str(e)})
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    
    return jsonify({'results': results, 'total_processed': len(results)})

@app.route('/heatmap', methods=['POST'])
def generate_heatmap():
    """Generate attention heatmap showing suspicious regions"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    
    try:
        heatmap_result = generate_attention_heatmap(filename)
        return jsonify(heatmap_result)
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@app.route('/compare', methods=['POST'])
def compare_videos():
    """Compare two videos/images side by side"""
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'error': 'Two files required'}), 400
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    if file1.filename == '' or file2.filename == '':
        return jsonify({'error': 'Both files must be selected'}), 400
    
    filename1 = os.path.join(app.config['UPLOAD_FOLDER'], 'compare_1_' + file1.filename)
    filename2 = os.path.join(app.config['UPLOAD_FOLDER'], 'compare_2_' + file2.filename)
    
    file1.save(filename1)
    file2.save(filename2)
    
    try:
        # Process both files - support images and videos
        is_image1 = is_allowed_image(filename1)
        is_image2 = is_allowed_image(filename2)
        is_video1 = is_allowed_video(filename1)
        is_video2 = is_allowed_video(filename2)
        
        # Process file 1
        if is_image1:
            result1 = process_image(filename1)
        elif is_video1:
            result1 = process_video(filename1)
        else:
            return jsonify({'error': f'Unsupported file type for {file1.filename}'}), 400
        
        # Process file 2
        if is_image2:
            result2 = process_image(filename2)
        elif is_video2:
            result2 = process_video(filename2)
        else:
            return jsonify({'error': f'Unsupported file type for {file2.filename}'}), 400
        
        # Handle errors
        if 'error' in result1 or 'error' in result2:
            return jsonify({
                'error': result1.get('error', result2.get('error'))
            }), 400
        
        # Calculate comparison metrics
        conf1 = result1.get('overall_confidence', 0)
        conf2 = result2.get('overall_confidence', 0)
        pred1 = result1.get('overall_prediction', 'UNKNOWN')
        pred2 = result2.get('overall_prediction', 'UNKNOWN')
        
        comparison = {
            'file1': {
                'name': file1.filename,
                'type': 'image' if is_image1 else 'video',
                'prediction': pred1,
                'confidence': conf1,
                'faces_detected': result1.get('faces_detected', 0),
                'frames_analyzed': result1.get('frames_analyzed', 0),
                'processed_image': result1.get('processed_image', '')
            },
            'file2': {
                'name': file2.filename,
                'type': 'image' if is_image2 else 'video',
                'prediction': pred2,
                'confidence': conf2,
                'faces_detected': result2.get('faces_detected', 0),
                'frames_analyzed': result2.get('frames_analyzed', 0),
                'processed_image': result2.get('processed_image', '')
            },
            'comparison': {
                'confidence_difference': abs(conf1 - conf2),
                'verdict_match': pred1 == pred2,
                'both_uncertain': pred1 == 'UNCERTAIN' and pred2 == 'UNCERTAIN',
                'summary': f"File 1: {pred1} ({conf1:.1f}%), File 2: {pred2} ({conf2:.1f}%)"
            }
        }
        
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': f'Comparison failed: {str(e)}'}), 500
    finally:
        for f in [filename1, filename2]:
            if os.path.exists(f):
                os.remove(f)

@app.route('/temporal-analysis', methods=['POST'])
def temporal_analysis():
    """Analyze video frame by frame for temporal inconsistencies"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    
    try:
        temporal_data = analyze_temporal_consistency(filename)
        return jsonify(temporal_data)
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@app.route('/training-samples')
def get_training_samples():
    """Get sample images from training data for reference"""
    metadata_path = './train_sample_videos/metadata.json'
    samples = {'fake_samples': [], 'real_samples': []}
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        for video_name, info in metadata.items():
            video_id = video_name.split('.')[0]
            faces_dir = f'train_sample_videos/{video_id}/faces'
            
            if os.path.exists(faces_dir):
                face_files = sorted(os.listdir(faces_dir))[:3]  # Get first 3 faces
                for face_file in face_files:
                    # Convert file path to base64 image data to avoid 404 issues
                    img_path = os.path.join(faces_dir, face_file)
                    try:
                        with open(img_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        
                        sample = {
                            'video_id': video_id,
                            'label': info['label'],
                            'original': info.get('original'),
                            'image_data': f'data:image/png;base64,{img_data}'
                        }
                        
                        if info['label'] == 'FAKE':
                            samples['fake_samples'].append(sample)
                        else:
                            samples['real_samples'].append(sample)
                    except Exception as e:
                        print(f"Error loading {img_path}: {e}")
    
    return jsonify(samples)

@app.route('/set-threshold', methods=['POST'])
def set_threshold():
    """Adjust detection threshold for sensitivity"""
    global DETECTION_THRESHOLD
    data = request.get_json()
    threshold = float(data.get('threshold', 0.5))
    
    # Clamp between 0.1 and 0.9
    DETECTION_THRESHOLD = max(0.1, min(0.9, threshold))
    
    return jsonify({
        'threshold': DETECTION_THRESHOLD,
        'message': f'Detection threshold set to {DETECTION_THRESHOLD:.2f}'
    })

@app.route('/stats')
def get_stats():
    """Get dataset statistics"""
    # Count actual dataset images
    train_fake = len([f for f in os.listdir('split_dataset_quick/train/fake') if f.endswith(('.jpg', '.png'))]) if os.path.exists('split_dataset_quick/train/fake') else 0
    train_real = len([f for f in os.listdir('split_dataset_quick/train/real') if f.endswith(('.jpg', '.png'))]) if os.path.exists('split_dataset_quick/train/real') else 0
    val_fake = len([f for f in os.listdir('split_dataset_quick/valid/fake') if f.endswith(('.jpg', '.png'))]) if os.path.exists('split_dataset_quick/valid/fake') else 0
    val_real = len([f for f in os.listdir('split_dataset_quick/valid/real') if f.endswith(('.jpg', '.png'))]) if os.path.exists('split_dataset_quick/valid/real') else 0
    test_fake = len([f for f in os.listdir('split_dataset_quick/test/fake') if f.endswith(('.jpg', '.png'))]) if os.path.exists('split_dataset_quick/test/fake') else 0
    test_real = len([f for f in os.listdir('split_dataset_quick/test/real') if f.endswith(('.jpg', '.png'))]) if os.path.exists('split_dataset_quick/test/real') else 0
    
    stats = {
        'model_loaded': model is not None,
        'model_path': MODEL_PATH,
        'detection_threshold': DETECTION_THRESHOLD,
        'uncertainty_range': UNCERTAINTY_RANGE,
        'dataset_info': {
            'train_samples': train_fake + train_real,
            'train_fake': train_fake,
            'train_real': train_real,
            'val_samples': val_fake + val_real,
            'val_fake': val_fake,
            'val_real': val_real,
            'test_samples': test_fake + test_real,
            'test_fake': test_fake,
            'test_real': test_real,
            'total_samples': train_fake + train_real + val_fake + val_real + test_fake + test_real
        }
    }
    return jsonify(stats)

if __name__ == '__main__':
    load_detection_model()
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
