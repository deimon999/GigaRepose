"""
Properly train the deepfake detection model
Run this script and let it complete - it will take 2-4 hours but will give you a working model
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF warnings

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2  # Faster than EfficientNet
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import tensorflow as tf

# Use smaller model for faster training
print("=" * 70)
print("DEEPFAKE DETECTOR - PROPER TRAINING")
print("Using MobileNetV2 (faster) with 10k dataset")
print("Expected time: 2-3 hours | Expected accuracy: 85-95%")
print("=" * 70)

# Settings
IMG_SIZE = 96  # Smaller for speed
BATCH_SIZE = 64
EPOCHS = 50
DATASET = 'split_dataset_quick'

# Data augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True,
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    f'{DATASET}/train',
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary'
)

val_gen = val_datagen.flow_from_directory(
    f'{DATASET}/valid',
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary'
)

print(f"\nTraining samples: {train_gen.samples}")
print(f"Validation samples: {val_gen.samples}")
print(f"Class mapping: {train_gen.class_indices}")

# Build model
base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)

# Freeze base model initially
base_model.trainable = False

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("\n" + "=" * 70)
print("PHASE 1: Training classifier head (10-15 min)")
print("=" * 70)

os.makedirs('./tmp_checkpoint', exist_ok=True)

# Phase 1: Train top layers
history1 = model.fit(
    train_gen,
    epochs=10,
    validation_data=val_gen,
    verbose=1
)

# Phase 2: Fine-tune
print("\n" + "=" * 70)
print("PHASE 2: Fine-tuning all layers (90-120 min)")
print("=" * 70)

base_model.trainable = True
model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

callbacks = [
    EarlyStopping(
        monitor='val_accuracy',
        patience=8,
        restore_best_weights=True,
        verbose=1
    ),
    ModelCheckpoint(
        './tmp_checkpoint/best_model.h5',
        monitor='val_accuracy',
        mode='max',
        save_best_only=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=0.00001,
        verbose=1
    )
]

history2 = model.fit(
    train_gen,
    epochs=EPOCHS,
    validation_data=val_gen,
    callbacks=callbacks,
    verbose=1
)

# Evaluate
print("\n" + "=" * 70)
print("TRAINING COMPLETE!")
print("=" * 70)

best_val_acc = max(history2.history['val_accuracy'])
print(f"\nBest Validation Accuracy: {best_val_acc*100:.2f}%")
print(f"Model saved to: ./tmp_checkpoint/best_model.h5")
print("\nYou can now use the web app with the trained model!")
print("The model should correctly detect fake vs real images.")
