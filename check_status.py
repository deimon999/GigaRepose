"""
Quick Training Status Checker
Shows current progress of model training
"""

import time
import os
from pathlib import Path

def check_status():
    print("=" * 60)
    print("TRAINING STATUS")
    print("=" * 60)
    print()
    
    # Check if training is running
    checkpoint_dir = Path('./tmp_checkpoint')
    model_file = checkpoint_dir / 'best_model.h5'
    
    if not checkpoint_dir.exists():
        print("❌ Training not started yet")
        print("\nStart training with: python 03-train_cnn.py --quick")
        return
    
    if model_file.exists():
        # Get model file info
        mod_time = model_file.stat().st_mtime
        file_size = model_file.stat().st_size / (1024 * 1024)  # MB
        age = time.time() - mod_time
        
        print(f"✓ Model saved: best_model.h5 ({file_size:.1f} MB)")
        print(f"  Last updated: {int(age)} seconds ago")
        
        if age < 30:
            print("\n🔄 Training is ACTIVE (model recently updated)")
        elif age < 300:
            print("\n⏳ Training likely in progress...")
        else:
            print("\n✅ Training appears COMPLETE")
    else:
        print("⏳ Training started but no model saved yet")
        print("   (waiting for first epoch to complete)")
    
    print()
    
    # Check dataset
    quick_dataset = Path('./split_dataset_quick')
    if quick_dataset.exists():
        train_count = len(list((quick_dataset / 'train' / 'real').glob('*.jpg')))
        train_count += len(list((quick_dataset / 'train' / 'fake').glob('*.jpg')))
        print(f"📊 Training on: {train_count:,} images (quick mode)")
    
    # Try to read last few lines of any log
    log_files = ['training_log.txt', 'training.log']
    for log in log_files:
        if Path(log).exists():
            try:
                with open(log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                # Look for epoch info
                for line in reversed(lines[-50:]):
                    if 'Epoch' in line and '/' in line:
                        print(f"\n📈 Latest progress:")
                        print(f"   {line.strip()}")
                        
                    if 'val_accuracy' in line:
                        # Extract accuracy
                        try:
                            parts = line.split('val_accuracy:')
                            if len(parts) > 1:
                                acc = float(parts[1].split()[0])
                                print(f"   Validation Accuracy: {acc*100:.2f}%")
                                break
                        except:
                            pass
                break
            except:
                pass
    
    print()
    print("-" * 60)
    
    # Estimate completion
    if model_file.exists() and age < 300:
        print("\n⏱  Estimated time remaining: 20-40 minutes")
        print("   (depends on current epoch)")
    elif model_file.exists():
        print("\n✅ Training complete! Next steps:")
        print("   1. Run web app: python app.py")
        print("   2. Test your fake image")
    
    print()

if __name__ == '__main__':
    check_status()
