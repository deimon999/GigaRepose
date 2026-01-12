"""
Real-time Training Monitor
Displays live training progress and statistics
"""

import os
import time
import re
from pathlib import Path
from datetime import datetime, timedelta

def parse_progress(line):
    """Extract progress information from training output"""
    # Match patterns like: "5/3125 ==================== 53:34 1s/step - accuracy: 0.4786 - loss: 2.5192"
    pattern = r'(\d+)/(\d+).*?(\d+:\d+:\d+|\d+:\d+).*?accuracy:\s*([\d.]+).*?loss:\s*([\d.]+)'
    match = re.search(pattern, line)
    if match:
        return {
            'step': int(match.group(1)),
            'total_steps': int(match.group(2)),
            'eta': match.group(3),
            'accuracy': float(match.group(4)),
            'loss': float(match.group(5))
        }
    return None

def parse_epoch(line):
    """Extract epoch information"""
    # Match patterns like: "Epoch 1/30"
    pattern = r'Epoch (\d+)/(\d+)'
    match = re.search(pattern, line)
    if match:
        return {
            'current': int(match.group(1)),
            'total': int(match.group(2))
        }
    return None

def parse_validation(line):
    """Extract validation metrics"""
    # Match patterns like: "val_accuracy: 0.8523 - val_loss: 0.3421"
    val_acc = re.search(r'val_accuracy:\s*([\d.]+)', line)
    val_loss = re.search(r'val_loss:\s*([\d.]+)', line)
    
    if val_acc and val_loss:
        return {
            'val_accuracy': float(val_acc.group(1)),
            'val_loss': float(val_loss.group(1))
        }
    return None

def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time(seconds):
    """Format seconds into human readable time"""
    return str(timedelta(seconds=int(seconds)))

print("=" * 70)
print("DEEPFAKE DETECTION - TRAINING MONITOR")
print("=" * 70)
print()

log_file = Path('./training_log.txt')

if not log_file.exists():
    print("❌ Training log file not found!")
    print("Make sure training is running with output redirected to training_log.txt")
    exit(1)

print("✓ Monitoring training progress...")
print("Press Ctrl+C to exit")
print()

# Track state
current_epoch = None
epoch_start_time = None
last_position = 0
epoch_history = []
best_val_acc = 0.0
best_epoch = 0

try:
    while True:
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                last_position = f.tell()
                
                for line in new_lines:
                    line = line.strip()
                    
                    # Check for epoch
                    epoch_info = parse_epoch(line)
                    if epoch_info:
                        current_epoch = epoch_info
                        epoch_start_time = time.time()
                        clear_screen()
                        print("=" * 70)
                        print(f"EPOCH {current_epoch['current']}/{current_epoch['total']}")
                        print("=" * 70)
                        print()
                    
                    # Check for progress
                    progress = parse_progress(line)
                    if progress and current_epoch:
                        pct = (progress['step'] / progress['total_steps']) * 100
                        bar_length = 40
                        filled = int(bar_length * progress['step'] / progress['total_steps'])
                        bar = '█' * filled + '░' * (bar_length - filled)
                        
                        print(f"\r{bar} {pct:5.1f}% | Step {progress['step']:4d}/{progress['total_steps']} | "
                              f"Acc: {progress['accuracy']:.4f} | Loss: {progress['loss']:.4f} | ETA: {progress['eta']}", 
                              end='', flush=True)
                    
                    # Check for validation metrics
                    val_metrics = parse_validation(line)
                    if val_metrics and current_epoch:
                        print()  # New line after progress bar
                        print()
                        print("-" * 70)
                        print(f"EPOCH {current_epoch['current']} COMPLETE")
                        print("-" * 70)
                        
                        # Calculate epoch time
                        if epoch_start_time:
                            epoch_time = time.time() - epoch_start_time
                            print(f"Time: {format_time(epoch_time)}")
                        
                        print(f"Validation Accuracy: {val_metrics['val_accuracy']:.4f} ({val_metrics['val_accuracy']*100:.2f}%)")
                        print(f"Validation Loss:     {val_metrics['val_loss']:.4f}")
                        
                        # Track best
                        if val_metrics['val_accuracy'] > best_val_acc:
                            best_val_acc = val_metrics['val_accuracy']
                            best_epoch = current_epoch['current']
                            print(f"🎯 NEW BEST MODEL! (Accuracy: {best_val_acc*100:.2f}%)")
                        
                        epoch_history.append({
                            'epoch': current_epoch['current'],
                            'val_acc': val_metrics['val_accuracy'],
                            'val_loss': val_metrics['val_loss']
                        })
                        
                        print()
                        
                        # Show history summary
                        if len(epoch_history) > 1:
                            print("Recent History:")
                            for i, h in enumerate(epoch_history[-5:], 1):
                                marker = "⭐" if h['epoch'] == best_epoch else "  "
                                print(f"{marker} Epoch {h['epoch']:2d}: Acc {h['val_acc']:.4f} | Loss {h['val_loss']:.4f}")
                        
                        print()
                        print(f"Best Model: Epoch {best_epoch} with {best_val_acc*100:.2f}% accuracy")
                        print("-" * 70)
                        print()
                    
                    # Check for early stopping
                    if "early stopping" in line.lower():
                        print()
                        print("=" * 70)
                        print("⚠ EARLY STOPPING TRIGGERED")
                        print("=" * 70)
                        print()
                    
                    # Check for completion
                    if "Total params:" in line:
                        print("\n📊 Model Architecture Loaded")
                    
                    if "Found" in line and "images belonging to" in line:
                        print(f"📁 {line}")
        
        time.sleep(2)  # Update every 2 seconds

except KeyboardInterrupt:
    print("\n\n" + "=" * 70)
    print("MONITORING STOPPED")
    print("=" * 70)
    print()
    if epoch_history:
        print(f"Training Progress Summary:")
        print(f"  Epochs completed: {len(epoch_history)}")
        print(f"  Best validation accuracy: {best_val_acc*100:.2f}% (Epoch {best_epoch})")
        print(f"  Latest validation accuracy: {epoch_history[-1]['val_acc']*100:.2f}%")
        print()
        print("Training is still running in the background.")
        print("Check training_log.txt for full details.")
    print()
