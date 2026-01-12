"""
Download 140k Real and Fake Faces dataset from Kaggle
Uses kagglehub for simple download without API credentials
"""

import os
import sys
import shutil
from pathlib import Path

print("=" * 60)
print("KAGGLE DATASET DOWNLOADER")
print("140k Real and Fake Faces Dataset")
print("=" * 60)
print()

# Install kagglehub if not available
try:
    import kagglehub
    print("✓ kagglehub is installed")
except ImportError:
    print("📦 Installing kagglehub...")
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'kagglehub'], check=True)
    import kagglehub
    print("✓ kagglehub installed successfully!")

print()
print("📥 Downloading dataset from Kaggle...")
print("This may take several minutes (dataset is ~3-4 GB)...")
print()

try:
    # Download the dataset
    # kagglehub will automatically handle authentication
    path = kagglehub.dataset_download("xhlulu/140k-real-and-fake-faces")
    
    print()
    print("=" * 60)
    print("✓ DOWNLOAD COMPLETE!")
    print("=" * 60)
    print(f"\nDataset downloaded to: {path}")
    
    # Check the structure
    print("\nDataset structure:")
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files[:3]:  # Show first 3 files only
            print(f'{subindent}{file}')
        if len(files) > 3:
            print(f'{subindent}... and {len(files) - 3} more files')
    
    # Count images
    print("\nCounting images...")
    real_path = Path(path) / "real_and_fake" / "real"
    fake_path = Path(path) / "real_and_fake" / "fake"
    
    # Try alternate structure
    if not real_path.exists():
        real_path = Path(path) / "real"
        fake_path = Path(path) / "fake"
    
    if real_path.exists() and fake_path.exists():
        real_count = len(list(real_path.glob("*.jpg"))) + len(list(real_path.glob("*.png")))
        fake_count = len(list(fake_path.glob("*.jpg"))) + len(list(fake_path.glob("*.png")))
        
        print(f"  Real images: {real_count:,}")
        print(f"  Fake images: {fake_count:,}")
        print(f"  Total: {real_count + fake_count:,}")
    
    print()
    print("=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print()
    print("The dataset is ready to use!")
    print()
    print("Option 1 - Integrate into your project:")
    print(f"  python 05-integrate_dataset.py")
    print()
    print("Option 2 - Use directly (update paths in scripts):")
    print(f"  Dataset location: {path}")
    print()
    
    # Ask if user wants to integrate now
    integrate = input("Would you like to integrate the dataset now? [y/n]: ").strip().lower()
    
    if integrate == 'y':
        print("\n" + "=" * 60)
        print("INTEGRATING DATASET")
        print("=" * 60)
        print()
        
        # Setup output directories
        dest_real = './prepared_dataset/real'
        dest_fake = './prepared_dataset/fake'
        os.makedirs(dest_real, exist_ok=True)
        os.makedirs(dest_fake, exist_ok=True)
        
        print("How many images per category?")
        print("Recommendations:")
        print("  - Quick test: 1000-2000")
        print("  - Good training: 5000-10000")
        print("  - Best results: 20000+")
        print()
        max_images = int(input("Images per category [default: 5000]: ").strip() or "5000")
        
        import random
        
        def copy_random_files(src, dst, max_files):
            """Copy random selection of files"""
            files = list(Path(src).glob("*.jpg")) + list(Path(src).glob("*.png"))
            files = random.sample(files, min(len(files), max_files))
            
            print(f"  Copying {len(files)} files...")
            for i, file in enumerate(files, 1):
                dst_file = Path(dst) / file.name
                shutil.copy2(file, dst_file)
                if i % 500 == 0:
                    print(f"    Progress: {i}/{len(files)}", end='\r')
            print(f"  ✓ Copied {len(files)} files")
            return len(files)
        
        print("\n📥 Copying real faces...")
        real_copied = copy_random_files(real_path, dest_real, max_images)
        
        print("\n📥 Copying fake faces...")
        fake_copied = copy_random_files(fake_path, dest_fake, max_images)
        
        print()
        print("=" * 60)
        print("✓ INTEGRATION COMPLETE!")
        print("=" * 60)
        print()
        print(f"Dataset Summary:")
        print(f"  Real images: {real_copied:,}")
        print(f"  Fake images: {fake_copied:,}")
        print(f"  Total: {real_copied + fake_copied:,}")
        print()
        print("📊 Next Steps:")
        print("  1. Split dataset:  python 02-prepare_fake_real_dataset.py")
        print("  2. Train model:    python 03-train_cnn.py")
        print("  3. Test web app:   python app.py")
        print()
    else:
        print("\nYou can integrate later by running:")
        print("  python 05-integrate_dataset.py")
    
except Exception as e:
    print()
    print("=" * 60)
    print("❌ ERROR")
    print("=" * 60)
    print(f"\n{str(e)}")
    print()
    print("If authentication is required:")
    print("1. Go to: https://www.kaggle.com/settings")
    print("2. Create API token (kaggle.json)")
    print("3. Place it in: C:\\Users\\<YourUsername>\\.kaggle\\")
    print()
    print("Or manually download from:")
    print("https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces")
    sys.exit(1)
