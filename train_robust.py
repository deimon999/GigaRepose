"""
Robust training script for DeepFake detection
With progress tracking and checkpoint saving
"""
import os
import json
import time
from datetime import datetime
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TF logging

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, Callback

# Configuration
IMG_SIZE = 96  # Increased for better accuracy
BATCH_SIZE = 24  # Adjusted for larger images
EPOCHS = 80  # More epochs
TRAIN_DIR = 'split_dataset/train'
VALID_DIR = 'split_dataset/valid'
CHECKPOINT_DIR = 'tmp_checkpoint'
PROGRESS_FILE = 'training_progress.json'

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

print("=" * 60)
print("DEEPFAKE DETECTION - ROBUST TRAINING")
print("=" * 60)
print(f"Image size: {IMG_SIZE}x{IMG_SIZE}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Max epochs: {EPOCHS}")
print("=" * 60)

# Data generators with enhanced augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.2,
    horizontal_flip=True,
    zoom_range=0.3,
    brightness_range=[0.85, 1.15],
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

# Build simpler, more stable model
def build_model():
    model = Sequential([
        # Block 1
        Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.25),
        
        # Block 2
        Conv2D(64, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.25),
        
        # Block 3
        Conv2D(128, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.25),
        
        # Block 4
        Conv2D(256, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.3),
        
        # Block 5
        Conv2D(512, (3, 3), activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        
        # Classifier
        Flatten(),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    return model

print("\n🏗️  Building model...")
model = build_model()
print(f"✓ Model compiled")
print(f"  Trainable params: {model.count_params():,}")

# Custom callback for progress tracking
class ProgressTracker(Callback):
    def __init__(self, progress_file):
        super().__init__()
        self.progress_file = progress_file
        self.start_time = time.time()
        
    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start = time.time()
        print(f"\n{'='*60}")
        print(f"Epoch {epoch + 1}/{EPOCHS}")
        print(f"{'='*60}")
        
    def on_epoch_end(self, epoch, logs=None):
        elapsed = time.time() - self.epoch_start
        total_elapsed = time.time() - self.start_time
        
        progress = {
            'epoch': epoch + 1,
            'total_epochs': EPOCHS,
            'loss': float(logs.get('loss', 0)),
            'accuracy': float(logs.get('accuracy', 0)),
            'val_loss': float(logs.get('val_loss', 0)),
            'val_accuracy': float(logs.get('val_accuracy', 0)),
            'precision': float(logs.get('precision', 0)),
            'recall': float(logs.get('recall', 0)),
            'epoch_time_seconds': int(elapsed),
            'total_time_seconds': int(total_elapsed),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save progress
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
        
        # Print summary
        print(f"\n📊 Epoch {epoch + 1} Summary:")
        print(f"  Loss: {logs.get('loss', 0):.4f} | Val Loss: {logs.get('val_loss', 0):.4f}")
        print(f"  Accuracy: {logs.get('accuracy', 0)*100:.2f}% | Val Accuracy: {logs.get('val_accuracy', 0)*100:.2f}%")
        print(f"  Precision: {logs.get('precision', 0):.4f} | Recall: {logs.get('recall', 0):.4f}")
        print(f"  Time: {int(elapsed)}s | Total: {int(total_elapsed)}s")

# Callbacks
callbacks = [
    ProgressTracker(PROGRESS_FILE),
    
    ModelCheckpoint(
        os.path.join(CHECKPOINT_DIR, 'best_model.h5'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    
    EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
]

# Train
print("\n" + "="*60)
print("STARTING TRAINING")
print("="*60)
print(f"Steps per epoch: {train_generator.n // BATCH_SIZE}")
print(f"Validation steps: {valid_generator.n // BATCH_SIZE}")
print("\nPress Ctrl+C to pause and save checkpoint")
print("="*60 + "\n")

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
    
    print("\n" + "="*60)
    print("TRAINING COMPLETED!")
    print("="*60)
    
    # Save final model
    model.save(os.path.join(CHECKPOINT_DIR, 'final_model.h5'))
    print(f"\n✓ Final model saved to {CHECKPOINT_DIR}/final_model.h5")
    
except KeyboardInterrupt:
    print("\n" + "="*60)
    print("TRAINING PAUSED")
    print("="*60)
    model.save(os.path.join(CHECKPOINT_DIR, 'interrupted_model.h5'))
    print(f"✓ Progress saved to {CHECKPOINT_DIR}/interrupted_model.h5")
    print("✓ You can resume training later")
