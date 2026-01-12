"""
Integrate FaceForensics++ or Kaggle dataset into your project
This script copies downloaded data into your prepared_dataset folder
"""

import os
import shutil
from pathlib import Path
import random

def copy_with_progress(src, dst, max_files=None):
    """Copy files with progress indicator"""
    files = list(Path(src).glob('**/*'))
    files = [f for f in files if f.is_file()]
    
    if max_files:
        files = random.sample(files, min(len(files), max_files))
    
    for i, file in enumerate(files, 1):
        dst_file = Path(dst) / file.name
        shutil.copy2(file, dst_file)
        if i % 100 == 0:
            print(f"  Copied {i}/{len(files)} files...", end='\r')
    
    print(f"  ✓ Copied {len(files)} files")
    return len(files)

print("=" * 60)
print("INTEGRATE DATASET INTO PROJECT")
print("=" * 60)
print()

# Ask which dataset source
print("Which dataset did you download?")
print("1. FaceForensics++ (from GitHub)")
print("2. Kaggle 140k Real and Fake Faces")
print("3. Other (manual setup)")
print()

choice = input("Choice [1/2/3]: ").strip()

if choice == '1':
    # FaceForensics++ integration
    print("\n📁 Looking for FaceForensics++ data...")
    
    ff_path = './FaceForensics'
    if not os.path.exists(ff_path):
        print("❌ FaceForensics folder not found")
        print("Please download the dataset first using: python 04-download_faceforensics.py")
        exit(1)
    
    # Common paths where faces might be
    possible_paths = [
        os.path.join(ff_path, 'original_sequences', 'youtube', 'c23', 'faces'),
        os.path.join(ff_path, 'manipulated_sequences', 'Deepfakes', 'c23', 'faces'),
        os.path.join(ff_path, 'manipulated_sequences', 'Face2Face', 'c23', 'faces'),
        os.path.join(ff_path, 'manipulated_sequences', 'FaceSwap', 'c23', 'faces'),
    ]
    
    print("\nAvailable data sources:")
    for p in possible_paths:
        if os.path.exists(p):
            count = len(list(Path(p).glob('**/*.png'))) + len(list(Path(p).glob('**/*.jpg')))
            print(f"  ✓ {os.path.basename(os.path.dirname(p))}: {count} images")
    
    # Setup output directories
    real_dir = './prepared_dataset/real'
    fake_dir = './prepared_dataset/fake'
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)
    
    print("\nHow many images to use per category? (recommended: 1000-5000)")
    max_per_category = int(input("Max images [default: 2000]: ").strip() or "2000")
    
    print("\n📥 Copying real faces...")
    real_path = os.path.join(ff_path, 'original_sequences', 'youtube', 'c23', 'faces')
    if os.path.exists(real_path):
        copy_with_progress(real_path, real_dir, max_per_category)
    
    print("\n📥 Copying fake faces...")
    fake_paths = [
        os.path.join(ff_path, 'manipulated_sequences', 'Deepfakes', 'c23', 'faces'),
        os.path.join(ff_path, 'manipulated_sequences', 'Face2Face', 'c23', 'faces'),
        os.path.join(ff_path, 'manipulated_sequences', 'FaceSwap', 'c23', 'faces'),
    ]
    
    for fake_path in fake_paths:
        if os.path.exists(fake_path):
            print(f"  From {os.path.basename(os.path.dirname(fake_path))}...")
            copy_with_progress(fake_path, fake_dir, max_per_category // 3)
    
elif choice == '2':
    # Kaggle dataset integration
    print("\n📁 Looking for Kaggle dataset...")
    
    # Common extraction paths
    possible_paths = [
        './downloaded_dataset',
        './140k-real-and-fake-faces',
        './real_and_fake',
    ]
    
    kaggle_path = None
    for p in possible_paths:
        if os.path.exists(p):
            kaggle_path = p
            break
    
    if not kaggle_path:
        print("❌ Kaggle dataset not found")
        print("\nPlease extract the dataset to one of these locations:")
        for p in possible_paths:
            print(f"  - {p}")
        exit(1)
    
    print(f"✓ Found dataset at: {kaggle_path}")
    
    # Kaggle dataset structure: real_and_fake/real/, real_and_fake/fake/
    source_real = os.path.join(kaggle_path, 'real_and_fake', 'real')
    source_fake = os.path.join(kaggle_path, 'real_and_fake', 'fake')
    
    if not os.path.exists(source_real):
        # Try alternate structure
        source_real = os.path.join(kaggle_path, 'real')
        source_fake = os.path.join(kaggle_path, 'fake')
    
    # Setup output directories
    dest_real = './prepared_dataset/real'
    dest_fake = './prepared_dataset/fake'
    os.makedirs(dest_real, exist_ok=True)
    os.makedirs(dest_fake, exist_ok=True)
    
    print("\nHow many images to use? (Kaggle has 140k total)")
    print("Recommended for training: 2000-10000 per category")
    max_images = int(input("Max images per category [default: 5000]: ").strip() or "5000")
    
    print("\n📥 Copying real faces...")
    real_count = copy_with_progress(source_real, dest_real, max_images)
    
    print("\n📥 Copying fake faces...")
    fake_count = copy_with_progress(source_fake, dest_fake, max_images)
    
else:
    print("\n📝 Manual Setup Instructions:")
    print("\n1. Create these directories:")
    print("   ./prepared_dataset/real/")
    print("   ./prepared_dataset/fake/")
    print("\n2. Copy your images:")
    print("   - Real images → ./prepared_dataset/real/")
    print("   - Fake images → ./prepared_dataset/fake/")
    print("\n3. Run the dataset preparation script:")
    print("   python 02-prepare_fake_real_dataset.py")
    exit(0)

print("\n" + "=" * 60)
print("✓ DATASET INTEGRATION COMPLETE!")
print("=" * 60)

# Count final images
real_count = len(list(Path('./prepared_dataset/real').glob('*.*')))
fake_count = len(list(Path('./prepared_dataset/fake').glob('*.*')))

print(f"\nDataset Summary:")
print(f"  Real images: {real_count}")
print(f"  Fake images: {fake_count}")
print(f"  Total: {real_count + fake_count}")

print("\n📊 Next Steps:")
print("  1. Split dataset: python 02-prepare_fake_real_dataset.py")
print("  2. Train model:   python 03-train_cnn.py")
print("  3. Test web app:  python app.py")
print()
