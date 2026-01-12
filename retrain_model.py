"""
Retrain Model with Improved Settings
This script retrains the deepfake detection model with better parameters
"""

import os
import sys

print("=" * 60)
print("RETRAINING DEEPFAKE DETECTION MODEL")
print("=" * 60)
print()
print("Improvements:")
print("✓ Increased data augmentation (rotation, zoom, brightness)")
print("✓ Fine-tuning last 20 layers of EfficientNet")
print("✓ Added extra dense layer (256 units)")
print("✓ Lower learning rate (0.00005)")
print("✓ Increased epochs to 50")
print("✓ Increased early stopping patience to 10")
print()
print("This will take several minutes...")
print()

# Run the training script
exit_code = os.system('python 03-train_cnn.py')

if exit_code == 0:
    print()
    print("=" * 60)
    print("✓ MODEL RETRAINED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("The new model should have better accuracy.")
    print("Restart the web application to use the updated model:")
    print("  python app.py")
else:
    print()
    print("✗ Training failed. Check the error messages above.")
    sys.exit(1)
