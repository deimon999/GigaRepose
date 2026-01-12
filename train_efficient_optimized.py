"""
EfficientNetB0 Transfer Learning - Optimized for CPU/Limited Memory
Target: 85-92% accuracy
"""
import os
import json
import time
from datetime import datetime
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, Callback
from tensorflow.keras.optimizers import Adam

# Optimized Configuration
IMG_SIZE = 128  # Reduced from 224 to 128 for memory efficiency
BATCH_SIZE = 8   # Smaller batches for CPU
EPOCHS = 80
LEARNING_RATE = 0.0001
TRAIN_DIR = 'split_dataset/train'
VALID_DIR = 'split_dataset/valid'
CHECKPOINT_DIR = 'tmp_checkpoint'
PROGRESS_FILE = 'training_progress.json'

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

print("=" * 70)
print("DEEPFAKE DETECTION - EFFICIENTNETB0 (OPTIMIZED)")
print("=" * 70)
print(f"Architecture: EfficientNetB0 (ImageNet pre-trained)")
print(f"Image size: {IMG_SIZE}x{IMG_SIZE} (optimized for CPU)")
print(f"Batch size: {BATCH_SIZE}")
print(f"Max epochs: {EPOCHS}")
print(f"Learning rate: {LEARNING_RATE}")
print("=" * 70)

# Advanced data augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.2,
    zoom_range=0.3,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],
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

# Build EfficientNetB0 model with smaller input
def build_efficientnet_model():
    print("\n🔨 Building EfficientNetB0 model...")
    
    # Load pre-trained EfficientNetB0
    base_model = EfficientNetB0(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    
    # Freeze base model
    base_model.trainable = False
    
    # Build model
    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dropout(0.5),
        Dense(256, activation='relu'),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print("✓ Model compiled successfully")
    print(f"✓ Total parameters: {model.count_params():,}")
    
    return model, base_model

model, base_model = build_efficientnet_model()

# Custom progress tracker
class ProgressTracker(Callback):
    def __init__(self, progress_file):
        super().__init__()
        self.progress_file = progress_file
        self.start_time = None
        
    def on_train_begin(self, logs=None):
        self.start_time = time.time()
        
    def on_epoch_end(self, epoch, logs=None):
        elapsed = time.time() - self.start_time
        epochs_done = epoch + 1
        epochs_remaining = EPOCHS - epochs_done
        time_per_epoch = elapsed / epochs_done
        estimated_remaining = time_per_epoch * epochs_remaining
        
        progress = {
            'current_epoch': epochs_done,
            'total_epochs': EPOCHS,
            'train_accuracy': float(logs.get('accuracy', 0)),
            'val_accuracy': float(logs.get('val_accuracy', 0)),
            'train_loss': float(logs.get('loss', 0)),
            'val_loss': float(logs.get('val_loss', 0)),
            'elapsed_time_sec': int(elapsed),
            'estimated_remaining_sec': int(estimated_remaining),
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'training',
            'architecture': 'EfficientNetB0',
            'image_size': IMG_SIZE
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
        
        hours_remaining = estimated_remaining / 3600
        print(f"\n⏱️  Estimated time remaining: {hours_remaining:.1f} hours")
        print(f"📊 Val Accuracy: {logs.get('val_accuracy', 0)*100:.2f}%")

# Callbacks
callbacks = [
    ProgressTracker(PROGRESS_FILE),
    
    ModelCheckpoint(
        os.path.join(CHECKPOINT_DIR, 'best_model_efficientnet.h5'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    
    ModelCheckpoint(
        os.path.join(CHECKPOINT_DIR, 'checkpoint_epoch_{epoch:02d}.h5'),
        save_freq='epoch',
        save_best_only=False,
        verbose=0
    ),
    
    EarlyStopping(
        monitor='val_accuracy',
        patience=15,
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

print("\n" + "=" * 70)
print("🚀 STARTING TRAINING - PHASE 1: Transfer Learning")
print("=" * 70)
print("Phase 1: Training top layers (base model frozen)")
print("This will train for 15 epochs, then fine-tune\n")

try:
    # Phase 1: Train with frozen base
    history_phase1 = model.fit(
        train_generator,
        validation_data=valid_generator,
        epochs=15,
        callbacks=callbacks,
        verbose=1
    )
    
    print("\n" + "=" * 70)
    print("🔓 PHASE 2: Fine-tuning")
    print("=" * 70)
    print("Unfreezing base model for fine-tuning...")
    
    # Phase 2: Unfreeze and fine-tune
    base_model.trainable = True
    
    # Freeze first 50 layers
    for layer in base_model.layers[:50]:
        layer.trainable = False
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE / 10),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"✓ Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    print("\n🚀 Resuming training with fine-tuning...\n")
    
    # Continue training
    history_phase2 = model.fit(
        train_generator,
        validation_data=valid_generator,
        epochs=EPOCHS,
        initial_epoch=15,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    final_model_path = os.path.join(CHECKPOINT_DIR, 'final_model_efficientnet.h5')
    model.save(final_model_path)
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print(f"✓ Best model: best_model_efficientnet.h5")
    print(f"✓ Final model: final_model_efficientnet.h5")
    print(f"✓ Final val accuracy: {history_phase2.history['val_accuracy'][-1]*100:.2f}%")
    print(f"✓ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Update progress
    with open(PROGRESS_FILE, 'r') as f:
        progress = json.load(f)
    
    progress['status'] = 'completed'
    progress['completion_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    progress['final_val_accuracy'] = float(history_phase2.history['val_accuracy'][-1])
    
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

except KeyboardInterrupt:
    print("\n\n⚠️  Training interrupted by user")
    interrupted_path = os.path.join(CHECKPOINT_DIR, 'interrupted_model_efficientnet.h5')
    model.save(interrupted_path)
    print(f"✓ Saved interrupted model: {interrupted_path}")
    
    # Update progress
    with open(PROGRESS_FILE, 'r') as f:
        progress = json.load(f)
    progress['status'] = 'interrupted'
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

except Exception as e:
    print(f"\n\n❌ Error during training: {str(e)}")
    error_path = os.path.join(CHECKPOINT_DIR, 'error_model_efficientnet.h5')
    try:
        model.save(error_path)
        print(f"✓ Saved model at error point: {error_path}")
    except:
        print("✗ Could not save model")
    raise

print("\n✓ Check progress: python check_training_progress.py")
