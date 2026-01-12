"""
Train on Full 140K Kaggle Dataset
==================================
Uses all 100k training images with augmentation for better accuracy.
Expected improvement: 64% → 75-85% with proper training.
"""

import os
import sys
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger
from tensorflow.keras.optimizers import Adam
import numpy as np
from datetime import datetime

# Configuration
IMG_SIZE = 64
BATCH_SIZE = 64  # Larger batch for better gradient estimates
EPOCHS = 50
INITIAL_LR = 0.001
DATASET_PATH = 'split_dataset'  # Full 140k dataset
CHECKPOINT_DIR = 'tmp_checkpoint'
LOG_FILE = 'training_log_full.txt'

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

print("=" * 60)
print("FULL DATASET TRAINING - 140K Images")
print("=" * 60)
print(f"Image size: {IMG_SIZE}x{IMG_SIZE}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Max epochs: {EPOCHS}")
print(f"Dataset: {DATASET_PATH}")
print("=" * 60)

# Check dataset exists
train_path = os.path.join(DATASET_PATH, 'train')
valid_path = os.path.join(DATASET_PATH, 'valid')
test_path = os.path.join(DATASET_PATH, 'test')

if not os.path.exists(train_path):
    print(f"\n❌ ERROR: Dataset not found at {DATASET_PATH}")
    print("Run: python 07-setup_kaggle_for_training.py")
    sys.exit(1)

# Count samples
train_fake = len([f for f in os.listdir(f'{train_path}/fake') if f.endswith(('.jpg', '.png'))])
train_real = len([f for f in os.listdir(f'{train_path}/real') if f.endswith(('.jpg', '.png'))])
val_fake = len([f for f in os.listdir(f'{valid_path}/fake') if f.endswith(('.jpg', '.png'))])
val_real = len([f for f in os.listdir(f'{valid_path}/real') if f.endswith(('.jpg', '.png'))])

print(f"\n📊 Dataset Summary:")
print(f"  Train: {train_fake + train_real:,} images ({train_fake:,} fake, {train_real:,} real)")
print(f"  Valid: {val_fake + val_real:,} images ({val_fake:,} fake, {val_real:,} real)")

# Data augmentation for training (helps generalization)
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Validation data (no augmentation)
valid_datagen = ImageDataGenerator(rescale=1./255)

# Load data
print(f"\n📂 Loading training data from {train_path}...")
train_generator = train_datagen.flow_from_directory(
    train_path,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=True
)

print(f"📂 Loading validation data from {valid_path}...")
valid_generator = valid_datagen.flow_from_directory(
    valid_path,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=False
)

print(f"\n✓ Label mapping: {train_generator.class_indices}")
print("  Expected: fake=0, real=1 (alphabetical order)")

# Build model with MobileNetV2 backbone
print("\n🏗️  Building model...")
base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)

# Freeze base model initially
base_model.trainable = False

# Add custom classification head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.5)(x)
x = Dense(64, activation='relu')(x)
x = Dropout(0.3)(x)
output = Dense(1, activation='sigmoid')(x)

model = Model(inputs=base_model.input, outputs=output)

# Compile
model.compile(
    optimizer=Adam(learning_rate=INITIAL_LR),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print(f"✓ Model compiled")
print(f"  Trainable params: {model.count_params():,}")

# Callbacks
callbacks = [
    ModelCheckpoint(
        filepath=os.path.join(CHECKPOINT_DIR, 'best_model.h5'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    EarlyStopping(
        monitor='val_accuracy',
        patience=8,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    ),
    CSVLogger(LOG_FILE, append=True)
]

# Phase 1: Train with frozen base
print("\n" + "=" * 60)
print("PHASE 1: Training with frozen MobileNetV2 base")
print("=" * 60)

history1 = model.fit(
    train_generator,
    epochs=15,
    validation_data=valid_generator,
    callbacks=callbacks,
    verbose=1
)

# Phase 2: Fine-tune top layers of base model
print("\n" + "=" * 60)
print("PHASE 2: Fine-tuning top MobileNetV2 layers")
print("=" * 60)

# Unfreeze last 30 layers
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

print(f"  Unfrozen last 30 layers")
print(f"  New trainable params: {model.count_params():,}")

# Recompile with lower learning rate
model.compile(
    optimizer=Adam(learning_rate=INITIAL_LR / 10),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

history2 = model.fit(
    train_generator,
    epochs=EPOCHS - 15,
    initial_epoch=15,
    validation_data=valid_generator,
    callbacks=callbacks,
    verbose=1
)

# Final evaluation
print("\n" + "=" * 60)
print("FINAL EVALUATION")
print("=" * 60)

test_datagen = ImageDataGenerator(rescale=1./255)
test_generator = test_datagen.flow_from_directory(
    test_path,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=False
)

test_loss, test_acc = model.evaluate(test_generator, verbose=1)

print(f"\n✓ Training complete!")
print(f"  Final test accuracy: {test_acc * 100:.2f}%")
print(f"  Model saved to: {CHECKPOINT_DIR}/best_model.h5")
print(f"  Training log: {LOG_FILE}")
print("\n" + "=" * 60)

# Log summary
with open(LOG_FILE, 'a') as f:
    f.write(f"\n\n{'='*60}\n")
    f.write(f"Training completed at {datetime.now()}\n")
    f.write(f"Final test accuracy: {test_acc * 100:.2f}%\n")
    f.write(f"Dataset: {DATASET_PATH} (140k images)\n")
    f.write(f"{'='*60}\n")

print("\n🎉 Training finished successfully!")
print("Run the web app to test: python app.py")
