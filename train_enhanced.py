"""
Improved CNN Training - Enhanced version for 85-90% accuracy
Larger images + deeper network + better augmentation
"""
import os
import json
import time
from datetime import datetime
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, Callback

# Enhanced Configuration
IMG_SIZE = 128  # Increased from 64 to 128
BATCH_SIZE = 16  # Adjusted for larger images
EPOCHS = 100  # More epochs
TRAIN_DIR = 'split_dataset/train'
VALID_DIR = 'split_dataset/valid'
CHECKPOINT_DIR = 'tmp_checkpoint'
PROGRESS_FILE = 'training_progress.json'

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

print("=" * 70)
print("DEEPFAKE DETECTION - ENHANCED CNN TRAINING")
print("=" * 70)
print(f"Image size: {IMG_SIZE}x{IMG_SIZE} (2x improvement)")
print(f"Batch size: {BATCH_SIZE}")
print(f"Max epochs: {EPOCHS}")
print(f"Target: 85-90% accuracy")
print("=" * 70)

# Enhanced data augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,          # More rotation
    width_shift_range=0.3,      # More shift
    height_shift_range=0.3,
    shear_range=0.2,            # Add shear
    zoom_range=0.3,             # More zoom
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],# Add brightness
    fill_mode='nearest'
)

valid_datagen = ImageDataGenerator(rescale=1./255)

print("\n📂 Loading training data...")
train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=True
)

print("📂 Loading validation data...")
valid_generator = valid_datagen.flow_from_directory(
    VALID_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=False
)

print(f"\n✓ Train samples: {train_generator.n}")
print(f"✓ Valid samples: {valid_generator.n}")
print(f"✓ Classes: {train_generator.class_indices}")

# Build deeper, more powerful model
def build_enhanced_model():
    model = Sequential([
        # Block 1 - 32 filters
        Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        BatchNormalization(),
        Conv2D(32, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.25),
        
        # Block 2 - 64 filters
        Conv2D(64, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        Conv2D(64, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.25),
        
        # Block 3 - 128 filters
        Conv2D(128, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        Conv2D(128, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.3),
        
        # Block 4 - 256 filters
        Conv2D(256, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        Conv2D(256, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.3),
        
        # Block 5 - 512 filters
        Conv2D(512, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        Conv2D(512, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.4),
        
        # Dense classifier
        Flatten(),
        Dense(1024, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),
        Dense(512, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),
        Dense(256, activation='relu'),
        Dropout(0.4),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    return model

print("\n🏗️  Building enhanced model...")
model = build_enhanced_model()
print(f"✓ Model compiled")
print(f"  Trainable params: {model.count_params():,}")
model.summary()

# Progress tracker
class ProgressTracker(Callback):
    def __init__(self, progress_file):
        super().__init__()
        self.progress_file = progress_file
        self.start_time = time.time()
        
    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start = time.time()
        print(f"\n{'='*70}")
        print(f"Epoch {epoch + 1}/{EPOCHS}")
        print(f"{'='*70}")
        
    def on_epoch_end(self, epoch, logs=None):
        elapsed = time.time() - self.epoch_start
        total_elapsed = time.time() - self.start_time
        epochs_remaining = EPOCHS - (epoch + 1)
        time_per_epoch = total_elapsed / (epoch + 1)
        est_remaining = time_per_epoch * epochs_remaining
        
        progress = {
            'current_epoch': epoch + 1,
            'total_epochs': EPOCHS,
            'train_accuracy': float(logs.get('accuracy', 0)),
            'val_accuracy': float(logs.get('val_accuracy', 0)),
            'train_loss': float(logs.get('loss', 0)),
            'val_loss': float(logs.get('val_loss', 0)),
            'precision': float(logs.get('precision', 0)),
            'recall': float(logs.get('recall', 0)),
            'epoch_time_sec': int(elapsed),
            'total_time_sec': int(total_elapsed),
            'est_remaining_sec': int(est_remaining),
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'training',
            'architecture': 'Enhanced_CNN',
            'image_size': IMG_SIZE
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
        
        print(f"\n📊 Epoch {epoch + 1} Summary:")
        print(f"  Loss: {logs.get('loss', 0):.4f} → Val Loss: {logs.get('val_loss', 0):.4f}")
        print(f"  Acc: {logs.get('accuracy', 0)*100:.2f}% → Val Acc: {logs.get('val_accuracy', 0)*100:.2f}%")
        print(f"  Precision: {logs.get('precision', 0):.4f} | Recall: {logs.get('recall', 0):.4f}")
        print(f"  ⏱️  Time: {int(elapsed)}s | Est remaining: {est_remaining/3600:.1f}h")

# Callbacks
callbacks = [
    ProgressTracker(PROGRESS_FILE),
    
    ModelCheckpoint(
        os.path.join(CHECKPOINT_DIR, 'best_model_enhanced.h5'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1,
        save_weights_only=False
    ),
    
    ModelCheckpoint(
        os.path.join(CHECKPOINT_DIR, 'checkpoint_epoch_{epoch:03d}_acc_{val_accuracy:.4f}.h5'),
        save_freq='epoch',
        period=10,  # Save every 10 epochs
        verbose=0
    ),
    
    EarlyStopping(
        monitor='val_accuracy',
        patience=20,  # More patience for 100 epochs
        restore_best_weights=True,
        mode='max',
        verbose=1
    ),
    
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=7,
        min_lr=1e-8,
        verbose=1
    )
]

# Train
print("\n" + "="*70)
print("🚀 STARTING ENHANCED TRAINING")
print("="*70)
print(f"Target: 85-90% accuracy")
print(f"Steps per epoch: {train_generator.n // BATCH_SIZE}")
print(f"Validation steps: {valid_generator.n // BATCH_SIZE}")
print(f"\nPress Ctrl+C to pause and save")
print("="*70 + "\n")

try:
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.n // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=valid_generator,
        validation_steps=valid_generator.n // BATCH_SIZE,
        callbacks=callbacks,
        verbose=1
    )
    
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETED!")
    print("="*70)
    
    final_path = os.path.join(CHECKPOINT_DIR, 'final_model_enhanced.h5')
    model.save(final_path)
    print(f"\n✓ Final model: {final_path}")
    print(f"✓ Final val accuracy: {history.history['val_accuracy'][-1]*100:.2f}%")
    print(f"✓ Best model: best_model_enhanced.h5")
    
    # Update progress
    with open(PROGRESS_FILE, 'r') as f:
        progress = json.load(f)
    progress['status'] = 'completed'
    progress['completion_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)
    
except KeyboardInterrupt:
    print("\n" + "="*70)
    print("⏸️  TRAINING PAUSED")
    print("="*70)
    interrupted_path = os.path.join(CHECKPOINT_DIR, 'interrupted_model_enhanced.h5')
    model.save(interrupted_path)
    print(f"✓ Progress saved: {interrupted_path}")
    
    with open(PROGRESS_FILE, 'r') as f:
        progress = json.load(f)
    progress['status'] = 'interrupted'
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

print("\n📊 Monitor: python check_training_progress.py")
