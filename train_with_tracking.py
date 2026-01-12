"""
DeepFake Detection - Full Dataset Training with Progress Tracking
Trains on 140k images with real-time monitoring and pause/resume support
"""

import os
import sys
import time
import json
import pickle
from datetime import datetime
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, Callback
from tensorflow.keras.optimizers import Adam

# GPU Configuration
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    try:
        for device in physical_devices:
            tf.config.experimental.set_memory_growth(device, True)
        print(f"✅ GPU Available: {len(physical_devices)} device(s)")
    except:
        pass
else:
    print("⚠️ No GPU found - Training on CPU (will be slower)")

# Configuration
IMG_SIZE = 64
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.0001

TRAIN_DIR = 'split_dataset/train'
VAL_DIR = 'split_dataset/valid'
TEST_DIR = 'split_dataset/test'

CHECKPOINT_DIR = 'tmp_checkpoint'
PROGRESS_FILE = 'training_progress.json'
MODEL_FILE = 'tmp_checkpoint/best_model.h5'
HISTORY_FILE = 'tmp_checkpoint/training_history.pkl'

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

class TrainingProgressTracker(Callback):
    """Custom callback to track and save training progress"""
    
    def __init__(self, progress_file):
        super().__init__()
        self.progress_file = progress_file
        self.start_time = time.time()
        self.epoch_times = []
        
    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start_time = time.time()
        
    def on_epoch_end(self, epoch, logs=None):
        epoch_time = time.time() - self.epoch_start_time
        self.epoch_times.append(epoch_time)
        
        # Calculate statistics
        elapsed_time = time.time() - self.start_time
        avg_epoch_time = np.mean(self.epoch_times)
        remaining_epochs = EPOCHS - (epoch + 1)
        estimated_remaining = avg_epoch_time * remaining_epochs
        
        # Progress data
        progress = {
            'current_epoch': epoch + 1,
            'total_epochs': EPOCHS,
            'progress_percent': ((epoch + 1) / EPOCHS) * 100,
            'train_loss': float(logs.get('loss', 0)),
            'train_accuracy': float(logs.get('accuracy', 0)),
            'val_loss': float(logs.get('val_loss', 0)),
            'val_accuracy': float(logs.get('val_accuracy', 0)),
            'learning_rate': float(self.model.optimizer.learning_rate.numpy()),
            'elapsed_time_seconds': elapsed_time,
            'elapsed_time_formatted': self.format_time(elapsed_time),
            'avg_epoch_time_seconds': avg_epoch_time,
            'avg_epoch_time_formatted': self.format_time(avg_epoch_time),
            'estimated_remaining_seconds': estimated_remaining,
            'estimated_remaining_formatted': self.format_time(estimated_remaining),
            'estimated_total_time': self.format_time(elapsed_time + estimated_remaining),
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'training'
        }
        
        # Save progress
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
        
        # Print progress
        print(f"\n{'='*80}")
        print(f"📊 EPOCH {epoch + 1}/{EPOCHS} COMPLETE")
        print(f"{'='*80}")
        print(f"Progress: {progress['progress_percent']:.1f}%")
        print(f"Train - Loss: {logs['loss']:.4f}, Accuracy: {logs['accuracy']:.4f}")
        print(f"Valid - Loss: {logs['val_loss']:.4f}, Accuracy: {logs['val_accuracy']:.4f}")
        print(f"Learning Rate: {progress['learning_rate']:.6f}")
        print(f"Elapsed: {progress['elapsed_time_formatted']}")
        print(f"Remaining: {progress['estimated_remaining_formatted']}")
        print(f"Total Est.: {progress['estimated_total_time']}")
        print(f"{'='*80}\n")
        
    def format_time(self, seconds):
        """Format seconds into readable time string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"
    
    def on_train_end(self, logs=None):
        # Mark training as complete
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
            progress['status'] = 'completed'
            progress['completion_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        
        total_time = time.time() - self.start_time
        print(f"\n{'='*80}")
        print(f"🎉 TRAINING COMPLETED!")
        print(f"Total Time: {self.format_time(total_time)}")
        print(f"{'='*80}\n")

def load_checkpoint():
    """Load checkpoint if exists"""
    if os.path.exists(MODEL_FILE) and os.path.exists(HISTORY_FILE):
        print(f"\n📁 Found existing checkpoint at {MODEL_FILE}")
        response = input("Resume from checkpoint? (y/n): ").strip().lower()
        if response == 'y':
            try:
                model = keras.models.load_model(MODEL_FILE)
                with open(HISTORY_FILE, 'rb') as f:
                    history = pickle.load(f)
                print("✅ Checkpoint loaded successfully!")
                return model, history
            except Exception as e:
                print(f"❌ Error loading checkpoint: {e}")
                print("Starting fresh training...")
    return None, None

def create_model():
    """Create MobileNetV2 model"""
    print("\n🔨 Building model...")
    
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model layers
    base_model.trainable = False
    
    # Add custom classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(1, activation='sigmoid')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print("✅ Model built successfully!")
    return model

def main():
    print("\n" + "="*80)
    print("🎯 DeepFake Detection - Full Dataset Training")
    print("="*80)
    
    # Check dataset
    print(f"\n📂 Dataset:")
    print(f"  Train: {TRAIN_DIR}")
    print(f"  Valid: {VAL_DIR}")
    print(f"  Test: {TEST_DIR}")
    
    # Data generators
    print("\n🔄 Setting up data generators...")
    
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        shear_range=0.2,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=True
    )
    
    validation_generator = val_datagen.flow_from_directory(
        VAL_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=False
    )
    
    print(f"\n📊 Dataset Statistics:")
    print(f"  Training samples: {train_generator.samples:,}")
    print(f"  Validation samples: {validation_generator.samples:,}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Steps per epoch: {train_generator.samples // BATCH_SIZE}")
    
    # Load or create model
    model, history = load_checkpoint()
    if model is None:
        model = create_model()
        history = None
    
    # Print model summary
    print("\n📋 Model Summary:")
    model.summary()
    
    # Callbacks
    print("\n⚙️ Setting up callbacks...")
    
    callbacks = [
        TrainingProgressTracker(PROGRESS_FILE),
        
        ModelCheckpoint(
            MODEL_FILE,
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
    
    # Initialize progress file
    initial_progress = {
        'current_epoch': 0,
        'total_epochs': EPOCHS,
        'progress_percent': 0,
        'status': 'starting',
        'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(initial_progress, f, indent=2)
    
    print("\n" + "="*80)
    print("🚀 STARTING TRAINING")
    print("="*80)
    print(f"⏱️  Estimated time: 15-30 hours on CPU, 2-4 hours on GPU")
    print(f"📝 Progress tracking: {PROGRESS_FILE}")
    print(f"💾 Model checkpoint: {MODEL_FILE}")
    print(f"\n💡 To pause: Press Ctrl+C")
    print(f"💡 To resume: Run this script again")
    print(f"💡 To monitor: Check {PROGRESS_FILE}")
    print("="*80 + "\n")
    
    time.sleep(3)
    
    try:
        # Train model
        history_new = model.fit(
            train_generator,
            epochs=EPOCHS,
            validation_data=validation_generator,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final history
        with open(HISTORY_FILE, 'wb') as f:
            pickle.dump(history_new.history, f)
        
        # Evaluate on test set
        print("\n" + "="*80)
        print("📊 EVALUATING ON TEST SET")
        print("="*80)
        
        test_datagen = ImageDataGenerator(rescale=1./255)
        test_generator = test_datagen.flow_from_directory(
            TEST_DIR,
            target_size=(IMG_SIZE, IMG_SIZE),
            batch_size=BATCH_SIZE,
            class_mode='binary',
            shuffle=False
        )
        
        test_loss, test_accuracy = model.evaluate(test_generator)
        
        print(f"\n🎯 Final Test Results:")
        print(f"  Loss: {test_loss:.4f}")
        print(f"  Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
        
        # Update progress with final results
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)
        progress['test_loss'] = float(test_loss)
        progress['test_accuracy'] = float(test_accuracy)
        progress['final_model'] = MODEL_FILE
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)
        
        print("\n✅ Training completed successfully!")
        print(f"📁 Model saved: {MODEL_FILE}")
        print(f"📊 Progress file: {PROGRESS_FILE}")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Training paused by user")
        print(f"💾 Model checkpoint saved: {MODEL_FILE}")
        print(f"📊 Progress saved: {PROGRESS_FILE}")
        print(f"▶️  To resume: Run this script again")
        
        # Update progress
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
            progress['status'] = 'paused'
            progress['pause_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress, f, indent=2)
        
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        
        # Update progress
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
            progress['status'] = 'error'
            progress['error'] = str(e)
            progress['error_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress, f, indent=2)
        
        sys.exit(1)

if __name__ == "__main__":
    main()
