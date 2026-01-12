"""
Download FaceForensics++ Dataset
This script helps you download the FaceForensics++ dataset and prepare it for training.
"""

import os
import subprocess
import sys

print("=" * 60)
print("FACEFORENSICS++ DATASET DOWNLOADER")
print("=" * 60)
print()

# Clone the repository if not already present
repo_path = './FaceForensics'
if not os.path.exists(repo_path):
    print("📥 Cloning FaceForensics++ repository...")
    subprocess.run(['git', 'clone', 'https://github.com/ondyari/FaceForensics.git'], check=True)
    print("✓ Repository cloned successfully!")
else:
    print("✓ FaceForensics++ repository already exists")

print()
print("=" * 60)
print("DATASET DOWNLOAD INSTRUCTIONS")
print("=" * 60)
print()
print("To download the FaceForensics++ dataset, you need to:")
print()
print("1. Fill out the access form:")
print("   https://github.com/ondyari/FaceForensics/blob/master/dataset/README.md")
print()
print("2. You will receive download credentials via email")
print()
print("3. Once you have credentials, use their download script:")
print()
print("   cd FaceForensics")
print("   python download-FaceForensics.py")
print()
print("   Available dataset options:")
print("   - Original sequences (real videos)")
print("   - Deepfakes")
print("   - Face2Face")
print("   - FaceSwap")
print("   - NeuralTextures")
print()
print("4. Recommended download command (extracted faces):")
print()
print("   python download-FaceForensics.py \\")
print("       -d all \\  # Download all manipulation types")
print("       -c c23 \\  # Compression level (c23=high quality)")
print("       -t faces  # Download extracted faces (saves time)")
print()
print("=" * 60)
print("ALTERNATIVE: SMALLER DATASET FOR QUICK START")
print("=" * 60)
print()
print("While waiting for FaceForensics++ access, you can use:")
print()
print("Option A - Kaggle Dataset (No approval needed):")
print("  1. Install: pip install kaggle")
print("  2. Setup Kaggle API: https://www.kaggle.com/docs/api")
print("  3. Download: kaggle datasets download -d xhlulu/140k-real-and-fake-faces")
print()
print("Option B - Manual download from Kaggle:")
print("  https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces")
print("  Extract to: ./downloaded_dataset/")
print()
print("=" * 60)

# Ask user which option they want
print()
choice = input("Would you like to:\n(1) Request FaceForensics++ access now\n(2) Use Kaggle dataset instead\n(3) Exit\n\nChoice [1/2/3]: ").strip()

if choice == '1':
    import webbrowser
    webbrowser.open('https://github.com/ondyari/FaceForensics/blob/master/dataset/README.md')
    print("\n✓ Opened access request page in your browser")
    print("After receiving credentials, run:")
    print("  cd FaceForensics")
    print("  python download-FaceForensics.py -d all -c c23 -t faces")
    
elif choice == '2':
    print("\n📦 Setting up Kaggle dataset download...")
    
    # Check if kaggle is installed
    try:
        import kaggle
        print("✓ Kaggle package is installed")
    except ImportError:
        print("Installing kaggle package...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'kaggle'], check=True)
        print("✓ Kaggle installed successfully!")
    
    print("\n⚠ You need to setup Kaggle API credentials first:")
    print("1. Go to: https://www.kaggle.com/settings")
    print("2. Click 'Create New API Token'")
    print("3. Save kaggle.json to: C:\\Users\\<YourUsername>\\.kaggle\\")
    print()
    
    setup = input("Have you setup Kaggle credentials? [y/n]: ").strip().lower()
    
    if setup == 'y':
        import webbrowser
        webbrowser.open('https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces')
        print("\n✓ Opened Kaggle dataset page")
        print("\nTo download via API, run:")
        print("  kaggle datasets download -d xhlulu/140k-real-and-fake-faces")
        print("  unzip 140k-real-and-fake-faces.zip -d downloaded_dataset")
    else:
        import webbrowser
        webbrowser.open('https://www.kaggle.com/settings')
        print("\n✓ Opened Kaggle settings page")
        print("After setting up credentials, rerun this script")
        
else:
    print("\n✓ Exiting. Run this script again when ready to download dataset.")
