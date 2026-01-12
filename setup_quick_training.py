"""
Quick training setup for fast results (under 1 hour)
Uses subset of data with optimized parameters
"""

import os
import shutil
from pathlib import Path
import random

print("=" * 60)
print("QUICK TRAINING SETUP (1 HOUR)")
print("=" * 60)
print()

# Source dataset
KAGGLE_CACHE = Path.home() / '.cache' / 'kagglehub' / 'datasets' / 'xhlulu' / '140k-real-and-fake-faces' / 'versions' / '2'
SOURCE = KAGGLE_CACHE / 'real_vs_fake' / 'real-vs-fake'

# Create quick training subset
QUICK_DATASET = Path('./split_dataset_quick')

# Remove old dataset
if QUICK_DATASET.exists():
    print("Removing old quick dataset...")
    shutil.rmtree(QUICK_DATASET)

print("Creating optimized dataset for 1-hour training...")
print()

# Optimal sizes for 1-hour training
TRAIN_SIZE = 5000  # Per category
VALID_SIZE = 1000  # Per category
TEST_SIZE = 500    # Per category

def copy_random_subset(src_real, src_fake, dst, count):
    """Copy random subset of images"""
    dst_real = dst / 'real'
    dst_fake = dst / 'fake'
    dst_real.mkdir(parents=True, exist_ok=True)
    dst_fake.mkdir(parents=True, exist_ok=True)
    
    # Copy real images
    real_files = list(src_real.glob('*.jpg'))
    selected_real = random.sample(real_files, min(len(real_files), count))
    for i, f in enumerate(selected_real, 1):
        shutil.copy2(f, dst_real / f.name)
        if i % 500 == 0:
            print(f"    Real: {i}/{count}", end='\r')
    print(f"    Real: {len(selected_real)} ✓")
    
    # Copy fake images
    fake_files = list(src_fake.glob('*.jpg'))
    selected_fake = random.sample(fake_files, min(len(fake_files), count))
    for i, f in enumerate(selected_fake, 1):
        shutil.copy2(f, dst_fake / f.name)
        if i % 500 == 0:
            print(f"    Fake: {i}/{count}", end='\r')
    print(f"    Fake: {len(selected_fake)} ✓")
    
    return len(selected_real), len(selected_fake)

print("📦 Creating training set (5000 per category)...")
train_real, train_fake = copy_random_subset(
    SOURCE / 'train' / 'real',
    SOURCE / 'train' / 'fake',
    QUICK_DATASET / 'train',
    TRAIN_SIZE
)

print("\n📦 Creating validation set (1000 per category)...")
valid_real, valid_fake = copy_random_subset(
    SOURCE / 'valid' / 'real',
    SOURCE / 'valid' / 'fake',
    QUICK_DATASET / 'valid',
    VALID_SIZE
)

print("\n📦 Creating test set (500 per category)...")
test_real, test_fake = copy_random_subset(
    SOURCE / 'test' / 'real',
    SOURCE / 'test' / 'fake',
    QUICK_DATASET / 'test',
    TEST_SIZE
)

print()
print("=" * 60)
print("✓ QUICK DATASET READY!")
print("=" * 60)
print()
print("Dataset summary:")
print(f"  Train: {train_real + train_fake:,} images ({train_real:,} real + {train_fake:,} fake)")
print(f"  Valid: {valid_real + valid_fake:,} images ({valid_real:,} real + {valid_fake:,} fake)")
print(f"  Test:  {test_real + test_fake:,} images ({test_real:,} real + {test_fake:,} fake)")
print()
print("Estimated training time: 45-60 minutes")
print()
print("Next step:")
print("  python 03-train_cnn.py --quick")
print()
