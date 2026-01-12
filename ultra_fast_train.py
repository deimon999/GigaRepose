"""
Ultra-fast training - uses tiny dataset (2k images) for quick results
Expected time: 10-15 minutes
Expected accuracy: 70-80%
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import shutil

print("=" * 70)
print("ULTRA-FAST TRAINING - 2K Dataset")
print("Time: 10-15 minutes | Accuracy: 70-80%")
print("=" * 70)

# Create smaller dataset
print("\nCreating 2K subset...")
import random
random.seed(42)

base_path = 'split_dataset_quick'
fast_path = 'split_dataset_fast'

for split in ['train', 'valid']:
    for cls in ['fake', 'real']:
        src = f'{base_path}/{split}/{cls}'
        dst = f'{fast_path}/{split}/{cls}'
        os.makedirs(dst, exist_ok=True)
        
        files = os.listdir(src)
        if split == 'train':
            sample_size = 800  # 800 per class = 1600 total
        else:
            sample_size = 200  # 200 per class = 400 total
            
        selected = random.sample(files, min(sample_size, len(files)))
        
        for f in selected:
            shutil.copy2(f'{src}/{f}', f'{dst}/{f}')
            
print("Subset created!")

# Training settings
IMG_SIZE = 64  # Smaller = faster
BATCH_SIZE = 32

train_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    horizontal_flip=True
).flow_from_directory(
    f'{fast_path}/train',
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary'
)

val_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(
    f'{fast_path}/valid',
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary'
)

print(f"\nTraining: {train_gen.samples} images")
print(f"Validation: {val_gen.samples} images")
print(f"Classes: {train_gen.class_indices}\n")

# Simple model
base = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet',
    pooling='avg'
)
base.trainable = False

model = Sequential([
    base,
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=Adam(0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("=" * 70)
print("Training (frozen base)...")
print("=" * 70)

os.makedirs('./tmp_checkpoint', exist_ok=True)

history = model.fit(
    train_gen,
    epochs=15,
    validation_data=val_gen,
    callbacks=[
        EarlyStopping(monitor='val_accuracy', patience=3, restore_best_weights=True),
        ModelCheckpoint('./tmp_checkpoint/best_model.h5', monitor='val_accuracy', save_best_only=True, mode='max')
    ],
    verbose=1
)

best_acc = max(history.history['val_accuracy'])
print(f"\n{'='*70}")
print(f"Training Complete! Best Accuracy: {best_acc*100:.1f}%")
print(f"Model saved to: ./tmp_checkpoint/best_model.h5")
print(f"{'='*70}")

# Cleanup
print("\nCleaning up temporary dataset...")
shutil.rmtree(fast_path)
print("Done! Restart the web app to use the new model.")
