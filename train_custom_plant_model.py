#!/usr/bin/env python3
"""
AgroNex-Pi: Custom Local Plant Model Trainer

Allows students to train a custom Edge AI model using their own real-world photos
(e.g., 30-50 photos of Money Plant, Money Tree, Hibiscus, Rose, Tulsi, etc.).

Features:
- MobileNetV2 Transfer Learning (starts from pre-trained ImageNet weights).
- Heavy real-time data augmentation (rotation, zoom, contrast, flip) so small datasets
  (30-50 photos) train effectively without overfitting.
- Exports a lightweight, quantized TensorFlow Lite (.tflite) model optimized for Raspberry Pi 4.
- Generates corresponding labels.txt and updates disease_db.

Usage:
  python train_custom_plant_model.py
  python train_custom_plant_model.py --data-dir field_dataset --epochs 8
  python train_custom_plant_model.py --overwrite-main  # Overwrites models/plant_model.tflite directly
"""

import os
import sys
import glob
import time
import argparse
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks

import config

IMG_SIZE = (224, 224)
BATCH_SIZE = 16


def list_images(folder):
    files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
        files.extend(glob.glob(os.path.join(folder, ext)))
    return files


LOCAL_DEMO_CLASSES = [
    "Local_healthy",
    "Local_unhealthy",
    "Local_yellow",
    "Local_dried",
    "background_not_a_leaf",
]


def create_augmented_dataset(data_dir, batch_size=BATCH_SIZE, force_local=True):
    """Loads images from subfolders and creates train/val splits with augmentation."""
    data_dir = os.path.abspath(data_dir)
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"Dataset directory '{data_dir}' does not exist.")

    # Check if local demonstration classes exist
    local_present = [c for c in LOCAL_DEMO_CLASSES if os.path.isdir(os.path.join(data_dir, c)) and len(list_images(os.path.join(data_dir, c))) >= 5]

    if force_local and len(local_present) >= 2:
        classes = sorted(local_present)
        print(f"\n[★] Selected Local Field Demonstration Classes ({len(classes)} classes):")
    else:
        # Fallback to any folders with >= 10 photos
        classes = [d for d in sorted(os.listdir(data_dir))
                   if os.path.isdir(os.path.join(data_dir, d)) and len(list_images(os.path.join(data_dir, d))) >= 10]

    if len(classes) < 2:
        raise ValueError(
            f"Need at least 2 class subfolders with at least 5 images each in '{data_dir}'. Found: {classes}"
        )

    print(f"\n[+] Active classes in '{data_dir}':")
    total_imgs = 0
    class_counts = []
    for c in classes:
        cnt = len(list_images(os.path.join(data_dir, c)))
        print(f"    - {c:28s}: {cnt:>3} images")
        total_imgs += cnt
        class_counts.append(cnt)

    print(f"[+] Total training dataset size: {total_imgs} images")

    # Balanced class weighting
    class_weights = {}
    for idx, cnt in enumerate(class_counts):
        class_weights[idx] = round(total_imgs / (len(classes) * cnt), 3)
    print(f"[+] Computed Balanced Class Weights: {class_weights}")

    # Load raw dataset using only the active classes
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        class_names=classes,
        validation_split=0.2,
        subset="training",
        seed=1337,
        image_size=IMG_SIZE,
        batch_size=batch_size,
        label_mode="int"
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        class_names=classes,
        validation_split=0.2,
        subset="validation",
        seed=1337,
        image_size=IMG_SIZE,
        batch_size=batch_size,
        label_mode="int"
    )

    # Real-time Data Augmentation pipeline (essential for robust field generalization)
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.15),
        layers.RandomTranslation(0.1, 0.1),
        layers.RandomContrast(0.15),
    ], name="data_augmentation")

    # MobileNetV2 normalisation: scale [0, 255] -> [-1, 1]
    rescale = layers.Rescaling(scale=1.0 / 127.5, offset=-1.0)

    train_ds = train_ds.map(lambda x, y: (data_augmentation(rescale(x), training=True), y),
                            num_parallel_calls=tf.data.AUTOTUNE)
    val_ds = val_ds.map(lambda x, y: (rescale(x), y),
                        num_parallel_calls=tf.data.AUTOTUNE)

    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds, classes, class_weights



def build_transfer_learning_model(num_classes):
    """Builds a MobileNetV2 transfer learning model."""
    print("[+] Downloading/Loading MobileNetV2 pre-trained on ImageNet...")
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False  # Freeze backbone for Phase 1

    inputs = layers.Input(shape=(224, 224, 3))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs)
    return model, base_model


def export_to_quantized_tflite(model, tflite_output_path):
    """Converts the Keras model to dynamic-range quantized TFLite."""
    print(f"\n[+] Quantizing model to TensorFlow Lite -> '{tflite_output_path}'...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    os.makedirs(os.path.dirname(os.path.abspath(tflite_output_path)), exist_ok=True)
    with open(tflite_output_path, "wb") as f:
        f.write(tflite_model)

    size_mb = os.path.getsize(tflite_output_path) / (1024 * 1024)
    print(f"[+] Exported Quantized TFLite: {size_mb:.2f} MB (Raspberry Pi 4 ready).")


def main():
    parser = argparse.ArgumentParser(description="Train Custom Plant Disease Model")
    parser.add_argument("--data-dir", type=str, default="field_dataset",
                        help="Folder containing class subdirectories with leaf photos")
    parser.add_argument("--epochs", type=int, default=8,
                        help="Number of epochs per training stage (default: 8)")
    parser.add_argument("--overwrite-main", action="store_true", default=True,
                        help="Overwrite models/plant_model.tflite directly as primary rover model (default: True)")
    args = parser.parse_args()

    print("=" * 65)
    print("      🌱  AGRONEX-PI CUSTOM PLANT MODEL TRAINER  🌱")
    print("=" * 65)

    data_dir = args.data_dir
    if not os.path.isabs(data_dir):
        data_dir = os.path.join(config.BASE_DIR, data_dir)

    # 1. Prepare Datasets
    try:
        train_ds, val_ds, classes, class_weights = create_augmented_dataset(data_dir)
    except Exception as e:
        print(f"\n❌ Dataset preparation error: {e}")
        sys.exit(1)

    num_classes = len(classes)

    # 2. Build Model
    model, base_model = build_transfer_learning_model(num_classes)
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    # 3. Phase 1 Training (Feature Extraction)
    print(f"\n[+] Phase 1: Training classification head ({args.epochs} epochs)...")
    early_stop = callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True)
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=[early_stop], class_weight=class_weights)

    # 4. Phase 2 Training (Fine-Tuning top backbone layers)
    print(f"\n[+] Phase 2: Fine-tuning top convolutional layers ({args.epochs} epochs)...")
    base_model.trainable = True
    # Freeze bottom 100 layers, fine-tune the rest
    for layer in base_model.layers[:100]:
        layer.trainable = False

    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=[early_stop], class_weight=class_weights)

    # 5. Determine Export Paths
    tflite_custom = os.path.join(config.BASE_DIR, "models", "custom_plant_model.tflite")
    labels_custom = os.path.join(config.BASE_DIR, "models", "custom_labels.txt")
    tflite_main = os.path.join(config.BASE_DIR, "models", "plant_model.tflite")
    labels_main = os.path.join(config.BASE_DIR, "models", "labels.txt")

    # 6. Save Labels File
    for l_path in [labels_custom, labels_main]:
        os.makedirs(os.path.dirname(l_path), exist_ok=True)
        with open(l_path, "w", encoding="utf-8") as f:
            for c in classes:
                f.write(c + "\n")
        print(f"[+] Saved labels ({len(classes)} classes) -> '{l_path}'")

    # 7. Export Quantized TFLite
    export_to_quantized_tflite(model, tflite_custom)
    import shutil
    shutil.copyfile(tflite_custom, tflite_main)
    print(f"[+] Synchronized to primary rover model -> '{tflite_main}'")

    print("\n" + "=" * 65)
    print("  🎉 TRAINING COMPLETE! CUSTOM MODEL IS READY FOR DEMONSTRATION")
    print("=" * 65)
    print(f"  Model  : {tflite_custom}")
    print(f"  Labels : {labels_custom}")
    print(f"  Classes: {', '.join(classes)}")
    print("\n  👉 TO TEST ON RASPBERRY PI OR PC CAMERA:")
    print("     python test_disease_camera.py")
    print("=" * 65 + "\n")



if __name__ == "__main__":
    main()
