"""
Quick retraining script with optimized settings for faster training
"""
import os
import sys
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

print("=" * 60)
print("OPTIMIZED QUICK TRAINING")
print("Strategy: Freeze base, unfreeze top, train head first")
print("=" * 60)

input_size = 128
batch_size = 128  # Larger batch for speed
dataset_path = 'split_dataset_quick'

# Data generators
train_datagen = ImageDataGenerator(
    rescale=1/255,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    zoom_range=0.1
)

val_datagen = ImageDataGenerator(rescale=1/255)

train_gen = train_datagen.flow_from_directory(
    os.path.join(dataset_path, 'train'),
    target_size=(input_size, input_size),
    batch_size=batch_size,
    class_mode='binary',
    shuffle=True
)

val_gen = val_datagen.flow_from_directory(
    os.path.join(dataset_path, 'valid'),
    target_size=(input_size, input_size),
    batch_size=batch_size,
    class_mode='binary',
    shuffle=False
)

print(f"\nDataset Info:")
print(f"Training samples: {train_gen.samples}")
print(f"Validation samples: {val_gen.samples}")
print(f"Steps per epoch: {len(train_gen)}")
print(f"Batch size: {batch_size}")

# Build model - freeze all base layers
efficient_net = EfficientNetB0(
    weights='imagenet',
    input_shape=(input_size, input_size, 3),
    include_top=False,
    pooling='max'
)

# Freeze all EfficientNet layers
for layer in efficient_net.layers:
    layer.trainable = False

model = Sequential([
    efficient_net,
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("\nModel Summary:")
model.summary()
print(f"\nTrainable parameters: {model.count_params():,}")

# Callbacks
os.makedirs('./tmp_checkpoint', exist_ok=True)
callbacks = [
    EarlyStopping(
        monitor='val_accuracy',
        patience=4,
        restore_best_weights=True,
        verbose=1
    ),
    ModelCheckpoint(
        './tmp_checkpoint/best_model.h5',
        monitor='val_accuracy',
        mode='max',
        save_best_only=True,
        verbose=1
    )
]

# Train
print("\n" + "=" * 60)
print("PHASE 1: Training dense layers only (fast)")
print("=" * 60)

history = model.fit(
    train_gen,
    epochs=20,
    validation_data=val_gen,
    callbacks=callbacks,
    verbose=1
)

print("\n" + "=" * 60)
print("Training Complete!")
print(f"Best validation accuracy: {max(history.history['val_accuracy'])*100:.2f}%")
print("=" * 60)
