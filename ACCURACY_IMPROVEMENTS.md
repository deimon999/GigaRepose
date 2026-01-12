# Quick Fixes for Detection Accuracy Issues

## Problem: Model Detecting Fake as Real

### Immediate Solutions (No Retraining):

#### 1. **Adjust Detection Threshold** ⚡ (Instant Fix)

The default threshold is 0.5. You can make it more sensitive:

**Via Web UI (Coming Soon):**
- Settings panel with threshold slider

**Via API:**
```bash
curl -X POST http://localhost:5000/set-threshold \
  -H "Content-Type: application/json" \
  -d '{"threshold": 0.4}'
```

**Recommended Thresholds:**
- `0.3-0.4`: Very sensitive (catches more fakes, but more false positives)
- `0.5`: Balanced (default)
- `0.6-0.7`: Conservative (fewer false positives, might miss some fakes)

#### 2. **Use Multiple Angles**
- Upload several images of the same person
- If ANY are detected as fake, investigate further

#### 3. **Check Attention Heatmap**
- Use the heatmap feature to see suspicious regions
- Look for artifacts around eyes, nose, mouth edges

---

### Long-term Solutions (Retraining Required):

#### 1. **Retrain with Improved Settings** ✓ (RECOMMENDED)

I've updated the training script with:
- ✅ More aggressive data augmentation
- ✅ Fine-tuning EfficientNet layers
- ✅ Additional dense layer (256 units)
- ✅ Lower learning rate (0.00005)
- ✅ 50 epochs instead of 20
- ✅ Better early stopping

**To retrain:**
```bash
python retrain_model.py
```

This takes 15-30 minutes but should significantly improve accuracy.

#### 2. **Collect More Training Data**

Current limitation: Only 25 training samples

**Options:**
- Download larger deepfake datasets:
  - [FaceForensics++](https://github.com/ondyari/FaceForensics)
  - [Celeb-DF](https://github.com/yuezunli/celeb-deepfakeforensics)
  - [DFDC (Facebook)](https://ai.facebook.com/datasets/dfdc/)

- Add your own samples:
  1. Place images in `prepared_dataset/fake/` or `prepared_dataset/real/`
  2. Run `python 02-prepare_fake_real_dataset.py`
  3. Run `python 03-train_cnn.py`

#### 3. **Use Ensemble Prediction**

Combine multiple models:
- Train same architecture 3-5 times
- Average their predictions
- More robust than single model

---

## Understanding the Current Model

**Training Stats:**
- Training samples: 25 faces
- Validation: 3 faces
- Test: 6 faces
- Total videos: 5 (4 fake, 1 real)

**Limitations:**
- Small dataset → Limited generalization
- May not recognize all deepfake techniques
- Best for face-swap type deepfakes

---

## Testing the Improved Model

After retraining, test with:

1. **Known fake images** - Should detect as FAKE
2. **Known real images** - Should detect as REAL
3. **Edge cases** - Poor lighting, angles, etc.

**Metrics to watch:**
- Validation accuracy should be > 80%
- Loss should decrease steadily
- No overfitting (train vs val loss similar)

---

## Emergency Workaround

If you need immediate results:

```python
# Temporarily modify app.py detection threshold
DETECTION_THRESHOLD = 0.35  # More sensitive

# Or use ensemble of multiple inferences
predictions = []
for _ in range(5):
    pred = model.predict(image)
    predictions.append(pred)
final_prediction = np.mean(predictions)
```

---

## Next Steps

1. ✅ **Try adjusting threshold first** (instant, no retraining)
2. ✅ **Retrain with improved settings** (`python retrain_model.py`)
3. ⏳ **Collect more training data** (time-consuming but best results)
4. ⏳ **Use ensemble methods** (advanced)

---

## Monitoring Improvements

Track these metrics:
- **False Positives** (real detected as fake)
- **False Negatives** (fake detected as real) ← Your current issue
- **True Positive Rate** (sensitivity)
- **True Negative Rate** (specificity)

---

## Additional Resources

- [Deepfake Detection Papers](https://github.com/aerophile/awesome-deepfakes-detection)
- [EfficientNet Documentation](https://keras.io/api/applications/efficientnet/)
- [Transfer Learning Guide](https://www.tensorflow.org/tutorials/images/transfer_learning)
