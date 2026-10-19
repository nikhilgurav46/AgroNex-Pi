# AgroNex-Pi Local Field Dataset

Drop your 30–50 photos of real-world local plants into these class folders:

## Recommended Folder Structure:
- `Money_Plant___healthy/` (30–50 photos of healthy money plant leaves)
- `Money_Plant___leaf_spot/` (30–50 photos of leaves with spots or brown lesions)
- `Money_Plant___yellowing/` (30–50 photos of yellowing/chlorotic leaves)
- `background_not_a_leaf/` (15–20 photos of pots, soil, table, or background)

## Photography Tips for High Accuracy:
1. **Angles**: Take photos from top-down, slight tilt (15–30°), and close-up (5–15 cm).
2. **Lighting**: Take some photos in sunlight, some in indoor room light.
3. **Variety**: Capture different leaves of the same plant (older bottom leaves and new top leaves).

## Training Command:
Once you put your photos in the folders above, run:
```bash
python train_custom_plant_model.py
```
This trains MobileNetV2 with data augmentation in ~2 minutes and creates:
- `models/custom_plant_model.tflite`
- `models/custom_labels.txt`

## Live Camera Demonstration:
```bash
python test_disease_camera.py --model models/custom_plant_model.tflite --labels models/custom_labels.txt
```
Or to make it the primary model for your rover & web dashboard:
```bash
python train_custom_plant_model.py --overwrite-main
```
