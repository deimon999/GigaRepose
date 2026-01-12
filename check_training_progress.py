"""
Monitor training progress in real-time
Run this script while training is happening to see live updates
"""

import json
import os
import time
from datetime import datetime

PROGRESS_FILE = 'training_progress.json'

def display_progress():
    """Display current training progress"""
    
    if not os.path.exists(PROGRESS_FILE):
        print("❌ No training progress found. Start training first!")
        return
    
    try:
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "="*80)
        print("📊 DEEPFAKE DETECTION - TRAINING PROGRESS")
        print("="*80)
        
        status = progress.get('status', 'unknown')
        status_emoji = {
            'starting': '🟡',
            'training': '🟢',
            'paused': '⏸️',
            'completed': '✅',
            'error': '❌'
        }
        
        print(f"\nStatus: {status_emoji.get(status, '⚪')} {status.upper()}")
        print(f"Last Update: {progress.get('last_update', 'N/A')}")
        
        # Progress bar
        current = progress.get('current_epoch', 0)
        total = progress.get('total_epochs', 50)
        percent = progress.get('progress_percent', 0)
        
        bar_length = 50
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\n📈 Progress:")
        print(f"  [{bar}] {percent:.1f}%")
        print(f"  Epoch: {current}/{total}")
        
        # Metrics
        if current > 0:
            print(f"\n📊 Current Metrics:")
            print(f"  Train Loss:     {progress.get('train_loss', 0):.4f}")
            print(f"  Train Accuracy: {progress.get('train_accuracy', 0):.4f} ({progress.get('train_accuracy', 0)*100:.2f}%)")
            print(f"  Val Loss:       {progress.get('val_loss', 0):.4f}")
            print(f"  Val Accuracy:   {progress.get('val_accuracy', 0):.4f} ({progress.get('val_accuracy', 0)*100:.2f}%)")
            print(f"  Learning Rate:  {progress.get('learning_rate', 0):.6f}")
        
        # Time estimates
        if 'elapsed_time_formatted' in progress:
            print(f"\n⏱️  Time:")
            print(f"  Elapsed:    {progress.get('elapsed_time_formatted', 'N/A')}")
            print(f"  Remaining:  {progress.get('estimated_remaining_formatted', 'N/A')}")
            print(f"  Total Est.: {progress.get('estimated_total_time', 'N/A')}")
            print(f"  Avg/Epoch:  {progress.get('avg_epoch_time_formatted', 'N/A')}")
        
        # Test results if completed
        if status == 'completed' and 'test_accuracy' in progress:
            print(f"\n🎯 Final Test Results:")
            print(f"  Test Loss:     {progress.get('test_loss', 0):.4f}")
            print(f"  Test Accuracy: {progress.get('test_accuracy', 0):.4f} ({progress.get('test_accuracy', 0)*100:.2f}%)")
            print(f"  Model saved:   {progress.get('final_model', 'N/A')}")
        
        # Pause/error info
        if status == 'paused':
            print(f"\n⏸️  Paused at: {progress.get('pause_time', 'N/A')}")
            print(f"  To resume: Run train_with_tracking.py again")
        
        if status == 'error':
            print(f"\n❌ Error occurred: {progress.get('error', 'Unknown error')}")
            print(f"  Error time: {progress.get('error_time', 'N/A')}")
        
        print("\n" + "="*80)
        print("Press Ctrl+C to exit monitoring")
        print("="*80 + "\n")
        
    except json.JSONDecodeError:
        print("❌ Error reading progress file. File may be corrupted.")
    except Exception as e:
        print(f"❌ Error: {e}")

def monitor_continuous():
    """Monitor progress continuously with auto-refresh"""
    print("Starting continuous monitoring...")
    print("Updates every 10 seconds. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            display_progress()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        monitor_continuous()
    else:
        display_progress()
        print("\n💡 Tip: Use 'python check_training_progress.py --continuous' for auto-refresh")
