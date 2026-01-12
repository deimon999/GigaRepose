"""
Reliable 6-Hour Training Script
- Uses 10k dataset for good accuracy
- Optimized settings for 6-hour completion
- Expected accuracy: 80-90%
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import time

start_time = time.time()

print("=" * 80)
print(" " * 20 + "DEEPFAKE DETECTOR - 6 HOUR TRAINING")
print("=" * 80)
print("Dataset: 10,000 training + 2,000 validation images")
print("Expected Time: 4-6 hours")
print("Expected Accuracy: 80-90%")
print("=" * 80)

# Optimized settings for speed + accuracy balance
IMG_SIZE = 96  # Good balance of speed and detail
BATCH_SIZE = 128  # Larger batches = faster training

# Data generators with moderate augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True,
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    'split_dataset_quick/train',
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=True
)

val_gen = val_datagen.flow_from_directory(
    'split_dataset_quick/valid',
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=False
)

print(f"\nDataset Loaded:")
print(f"  Training samples: {train_gen.samples:,}")
print(f"  Validation samples: {val_gen.samples:,}")
print(f"  Class mapping: {train_gen.class_indices}")
print(f"  Steps per epoch: {len(train_gen)}")
print(f"  Batch size: {BATCH_SIZE}")

# Build model
print("\nBuilding model...")
base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet',
    pooling='avg'
)

# Freeze base model for Phase 1
base_model.trainable = False

model = Sequential([
    base_model,
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("\nModel Architecture:")
model.summary()
print(f"\nTrainable parameters: {model.count_params():,}")

# Setup callbacks
os.makedirs('./tmp_checkpoint', exist_ok=True)

callbacks_phase1 = [
    EarlyStopping(
        monitor='val_accuracy',
        patience=5,
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
        patience=2,
        min_lr=0.00001,
        verbose=1
    )
]

# PHASE 1: Train head layers (fast)
print("\n" + "=" * 80)
print(" " * 25 + "PHASE 1: HEAD TRAINING")
print("=" * 80)
print("Training dense layers only (base frozen)")
print("Expected time: 30-60 minutes")
print("=" * 80 + "\n")

history1 = model.fit(
    train_gen,
    epochs=20,
    validation_data=val_gen,
    callbacks=callbacks_phase1,
    verbose=1
)

phase1_time = (time.time() - start_time) / 60
best_val_acc_phase1 = max(history1.history['val_accuracy'])
print(f"\nPhase 1 Complete!")
print(f"Time elapsed: {phase1_time:.1f} minutes")
print(f"Best validation accuracy: {best_val_acc_phase1*100:.2f}%")

# PHASE 2: Fine-tune (unfreeze and retrain with lower learning rate)
print("\n" + "=" * 80)
print(" " * 25 + "PHASE 2: FINE-TUNING")
print("=" * 80)
print("Unfreezing base model for fine-tuning")
print("Expected time: 3-5 hours")
print("=" * 80 + "\n")

# Unfreeze base model
base_model.trainable = True

# Recompile with lower learning rate
model.compile(
    optimizer=Adam(learning_rate=0.0001),  # 10x lower
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print(f"Trainable parameters after unfreezing: {model.count_params():,}\n")

callbacks_phase2 = [
    EarlyStopping(
        monitor='val_accuracy',
        patience=10,
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
        min_lr=0.000001,
        verbose=1
    )
]

history2 = model.fit(
    train_gen,
    epochs=50,  # Will early stop if not improving
    validation_data=val_gen,
    callbacks=callbacks_phase2,
    verbose=1
)

# Final results
total_time = (time.time() - start_time) / 60
best_val_acc = max(history2.history['val_accuracy'])

print("\n" + "=" * 80)
print(" " * 28 + "TRAINING COMPLETE!")
print("=" * 80)
print(f"Total time: {total_time/60:.2f} hours ({total_time:.1f} minutes)")
print(f"Best validation accuracy: {best_val_acc*100:.2f}%")
print(f"Model saved to: ./tmp_checkpoint/best_model.h5")
print("=" * 80)

# Test on validation set
print("\nFinal Evaluation on Validation Set:")
val_loss, val_acc = model.evaluate(val_gen, verbose=1)
print(f"Validation Accuracy: {val_acc*100:.2f}%")
print(f"Validation Loss: {val_loss:.4f}")

print("\n" + "=" * 80)
print("You can now use the web app with the trained model!")
print("Restart the Flask app if it's running:")
print("  python app.py")
print("=" * 80)
