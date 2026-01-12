"""
Use the already-split Kaggle dataset for training
Since the dataset comes pre-split into train/valid/test, we can use it directly
"""

import os
import shutil
from pathlib import Path

# The kagglehub download location
KAGGLE_CACHE = Path.home() / '.cache' / 'kagglehub' / 'datasets' / 'xhlulu' / '140k-real-and-fake-faces' / 'versions' / '2'
DATASET_SOURCE = KAGGLE_CACHE / 'real_vs_fake' / 'real-vs-fake'

print("=" * 60)
print("SETUP KAGGLE DATASET FOR TRAINING")
print("=" * 60)
print()

# Check if dataset exists
if not DATASET_SOURCE.exists():
    print("❌ Kaggle dataset not found!")
    print(f"Expected location: {DATASET_SOURCE}")
    print()
    print("Please run first: python 06-download_kaggle_dataset.py")
    exit(1)

print(f"✓ Found dataset at: {DATASET_SOURCE}")
print()

# The dataset is already split! Let's use it directly
print("Dataset structure:")
print(f"  Train: {DATASET_SOURCE / 'train'}")
print(f"  Valid: {DATASET_SOURCE / 'valid'}")
print(f"  Test:  {DATASET_SOURCE / 'test'}")
print()

# Count images
train_real = len(list((DATASET_SOURCE / 'train' / 'real').glob('*.jpg')))
train_fake = len(list((DATASET_SOURCE / 'train' / 'fake').glob('*.jpg')))
valid_real = len(list((DATASET_SOURCE / 'valid' / 'real').glob('*.jpg')))
valid_fake = len(list((DATASET_SOURCE / 'valid' / 'fake').glob('*.jpg')))
test_real = len(list((DATASET_SOURCE / 'test' / 'real').glob('*.jpg')))
test_fake = len(list((DATASET_SOURCE / 'test' / 'fake').glob('*.jpg')))

print("Image counts:")
print(f"  Train: {train_real:,} real + {train_fake:,} fake = {train_real + train_fake:,} total")
print(f"  Valid: {valid_real:,} real + {valid_fake:,} fake = {valid_real + valid_fake:,} total")
print(f"  Test:  {test_real:,} real + {test_fake:,} fake = {test_real + test_fake:,} total")
print()

# Option 1: Create symlinks (Windows 10+)
# Option 2: Copy files
print("Choose setup method:")
print("1. Create symbolic links (instant, saves space)")
print("2. Copy files to project (slower, uses more space)")
print()

choice = input("Choice [1/2, default: 1]: ").strip() or "1"

DEST = Path('./split_dataset')

if choice == "1":
    print("\n📌 Creating symbolic links...")
    
    # Remove old directory if exists
    if DEST.exists():
        print("  Removing old split_dataset...")
        shutil.rmtree(DEST)
    
    # Create directory structure
    DEST.mkdir(exist_ok=True)
    
    try:
        # Create symlinks for train/valid/test
        for split in ['train', 'valid', 'test']:
            src = DATASET_SOURCE / split
            dst = DEST / split
            
            # On Windows, need admin or developer mode for symlinks
            # Try junction (works without admin)
            import subprocess
            result = subprocess.run(
                ['mklink', '/J', str(dst.absolute()), str(src.absolute())],
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"  ✓ Linked {split}/")
            else:
                raise Exception(result.stderr)
        
        print("\n✓ Symbolic links created successfully!")
        print(f"\nYour split_dataset now points to: {DATASET_SOURCE}")
        
    except Exception as e:
        print(f"\n⚠ Could not create symbolic links: {e}")
        print("\nFalling back to copying files...")
        choice = "2"

if choice == "2":
    print("\n📁 Copying dataset files...")
    print("This will take several minutes...")
    print()
    
    # Ask how many images to copy
    print("How many images per category per split?")
    print("Full dataset:")
    print(f"  Train: {train_real:,} per category")
    print(f"  Valid: {valid_real:,} per category")
    print(f"  Test:  {test_real:,} per category")
    print()
    print("Recommendations:")
    print("  Quick test: 1000 train / 200 valid / 200 test")
    print("  Good model: 5000 train / 1000 valid / 1000 test")
    print("  Best model: all (50000 train / 10000 valid / 10000 test)")
    print()
    
    train_max = int(input(f"Train images per category [default: 5000]: ").strip() or "5000")
    valid_max = int(input(f"Valid images per category [default: 1000]: ").strip() or "1000")
    test_max = int(input(f"Test images per category [default: 1000]: ").strip() or "1000")
    
    import random
    
    def copy_images(src, dst, max_count, label):
        """Copy random selection of images"""
        dst.mkdir(parents=True, exist_ok=True)
        
        files = list(src.glob('*.jpg'))
        files = random.sample(files, min(len(files), max_count))
        
        for i, file in enumerate(files, 1):
            shutil.copy2(file, dst / file.name)
            if i % 100 == 0:
                print(f"    {label}: {i}/{len(files)}", end='\r')
        
        print(f"    {label}: {len(files)}/{len(files)} ✓")
        return len(files)
    
    # Remove old directory
    if DEST.exists():
        shutil.rmtree(DEST)
    
    totals = {}
    
    for split, max_count in [('train', train_max), ('valid', valid_max), ('test', test_max)]:
        print(f"\n  Copying {split}/...")
        
        real_count = copy_images(
            DATASET_SOURCE / split / 'real',
            DEST / split / 'real',
            max_count,
            f"{split}/real"
        )
        
        fake_count = copy_images(
            DATASET_SOURCE / split / 'fake',
            DEST / split / 'fake',
            max_count,
            f"{split}/fake"
        )
        
        totals[split] = {'real': real_count, 'fake': fake_count}
    
    print()
    print("=" * 60)
    print("✓ DATASET COPIED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Final counts:")
    for split in ['train', 'valid', 'test']:
        total = totals[split]['real'] + totals[split]['fake']
        print(f"  {split.capitalize()}: {totals[split]['real']:,} real + {totals[split]['fake']:,} fake = {total:,}")

print()
print("=" * 60)
print("READY TO TRAIN!")
print("=" * 60)
print()
print("Your dataset is ready at: ./split_dataset/")
print()
print("Next steps:")
print("  1. Train model: python 03-train_cnn.py")
print("  2. Test model:  python app.py")
print()
