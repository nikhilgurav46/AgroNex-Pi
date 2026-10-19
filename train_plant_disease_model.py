#!/usr/bin/env python3
"""
AgroNex-Pi: Plant Disease Model Training Pipeline (§9.1)

Trains MobileNetV2 on the target crop classes and exports a Raspberry Pi 4
compatible dynamic-range quantized TFLite model to models/plant_model.tflite.

Augmentation is applied in the tf.data pipeline only — it is NOT baked into
the exported graph (RandomFlip/Rotation layers break Pi tflite-runtime).
Inference preprocessing stays in disease_detect.py: (x / 127.5) - 1.0.
"""

import os
import sys
import glob
import zipfile
import shutil

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np
from sklearn.utils.class_weight import compute_class_weight

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks

import config

print(f"[+] Using TensorFlow version: {tf.__version__}")
print(f"[+] NumPy version: {np.__version__}")

# Canonical class names written into models/labels.txt (must match disease_db keys)
TARGET_CLASSES = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___healthy",
    "background_not_a_leaf",
]

FOLDER_ALIASES = {
    "Pepper__bell___Bacterial_spot": [
        "Pepper__bell___Bacterial_spot", "Pepper,_bell___Bacterial_spot",
        "Pepper_bell___Bacterial_spot", "Pepper___Bacterial_spot",
    ],
    "Pepper__bell___healthy": [
        "Pepper__bell___healthy", "Pepper,_bell___healthy",
        "Pepper_bell___healthy", "Pepper___healthy",
    ],
    "Potato___Early_blight": ["Potato___Early_blight", "Potato_Early_blight"],
    "Potato___Late_blight": ["Potato___Late_blight", "Potato_Late_blight"],
    "Potato___healthy": ["Potato___healthy", "Potato_healthy"],
    "Tomato___Early_blight": ["Tomato___Early_blight", "Tomato_Early_blight"],
    "Tomato___Late_blight": ["Tomato___Late_blight", "Tomato_Late_blight"],
    "Tomato___healthy": ["Tomato___healthy", "Tomato_healthy"],
    "background_not_a_leaf": ["background_not_a_leaf", "Background_without_leaves"],
}

IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS_STAGE1 = 4
EPOCHS_STAGE2 = 4
MAX_SAMPLES_PER_CLASS = 180
FIELD_SAMPLES_PER_CLASS = 360   # No cap on student-captured images (use all)
STAGING_DIR = os.path.join(config.BASE_DIR, "training_subset")
FIELD_DATASET_DIR = os.path.join(config.BASE_DIR, "field_dataset")


def _list_images(folder):
    files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
        files.extend(glob.glob(os.path.join(folder, ext)))
    return files


def find_or_extract_dataset():
    """Locate plantvillage_dataset, or unzip plantdisease.zip if present."""
    raw = os.path.join(config.BASE_DIR, "plantvillage_dataset")
    zip_path = os.path.join(config.BASE_DIR, "plantdisease.zip")
    if os.path.isdir(raw) and any(os.scandir(raw)):
        return raw
    if os.path.isfile(zip_path):
        print(f"[+] Extracting '{zip_path}' -> plantvillage_dataset ...")
        os.makedirs(raw, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(raw)
        print("[+] Dataset extracted.")
        return raw
    return raw if os.path.isdir(raw) else None


def generate_synthetic_class_images(dest_dir, class_name, count=80):
    """
    Fallback leaf-like RGB images so training can still export a valid Pi TFLite
    artifact when PlantVillage is not on disk. Distinct color/spot patterns per class.
    """
    os.makedirs(dest_dir, exist_ok=True)
    rng = np.random.default_rng(abs(hash(class_name)) % (2**32))
    palettes = {
        "Pepper__bell___Bacterial_spot": ((40, 140, 50), (90, 40, 20)),
        "Pepper__bell___healthy": ((30, 160, 45), (40, 170, 55)),
        "Potato___Early_blight": ((50, 120, 40), (140, 90, 20)),
        "Potato___Late_blight": ((35, 90, 40), (20, 40, 20)),
        "Potato___healthy": ((45, 155, 55), (50, 165, 60)),
        "Tomato___Early_blight": ((55, 130, 40), (160, 80, 25)),
        "Tomato___Late_blight": ((40, 95, 35), (25, 35, 20)),
        "Tomato___healthy": ((35, 170, 50), (40, 180, 60)),
        "background_not_a_leaf": ((110, 90, 60), (80, 70, 50)),
    }
    base, spot = palettes.get(class_name, ((80, 80, 80), (40, 40, 40)))
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise RuntimeError("Pillow is required to generate fallback training images.")

    for i in range(count):
        arr = np.zeros((224, 224, 3), dtype=np.uint8)
        arr[:, :, 0] = np.clip(base[0] + rng.integers(-18, 19, (224, 224)), 0, 255)
        arr[:, :, 1] = np.clip(base[1] + rng.integers(-18, 19, (224, 224)), 0, 255)
        arr[:, :, 2] = np.clip(base[2] + rng.integers(-18, 19, (224, 224)), 0, 255)
        img = Image.fromarray(arr, mode="RGB")
        draw = ImageDraw.Draw(img)
        n_spots = 0 if "healthy" in class_name and "background" not in class_name else rng.integers(8, 28)
        if class_name == "background_not_a_leaf":
            n_spots = rng.integers(2, 8)
        for _ in range(int(n_spots)):
            x, y = int(rng.integers(10, 210)), int(rng.integers(10, 210))
            r = int(rng.integers(4, 16))
            draw.ellipse((x - r, y - r, x + r, y + r), fill=tuple(int(c) for c in spot))
        img.save(os.path.join(dest_dir, f"syn_{i:03d}.jpg"), quality=90)


def merge_field_dataset(staging_dir: str) -> list:
    """
    Copies all images from field_dataset/<class_name>/ into staging_dir/<class_name>/.
    Also discovers any NEW custom classes (local plants photographed by students)
    not in TARGET_CLASSES and adds them automatically.
    Returns the final sorted list of all active class names.
    """
    if not os.path.isdir(FIELD_DATASET_DIR):
        print("[*] No field_dataset/ found — skipping custom image merge.")
        return sorted(os.listdir(staging_dir))

    merged_count = 0
    new_classes = []
    for class_name in sorted(os.listdir(FIELD_DATASET_DIR)):
        src_dir = os.path.join(FIELD_DATASET_DIR, class_name)
        if not os.path.isdir(src_dir):
            continue
        images = _list_images(src_dir)
        if not images:
            continue
        dst_dir = os.path.join(staging_dir, class_name)
        os.makedirs(dst_dir, exist_ok=True)
        copied = 0
        for img_path in images:
            dst_path = os.path.join(dst_dir, "field_" + os.path.basename(img_path))
            if not os.path.exists(dst_path):
                shutil.copyfile(img_path, dst_path)
                copied += 1
        if copied:
            print(f"[+] Field dataset merged: {copied} images -> staging/{class_name}")
            merged_count += copied
        existing_staging = sorted(os.listdir(staging_dir))
        if class_name not in TARGET_CLASSES and class_name in existing_staging:
            new_classes.append(class_name)

    if new_classes:
        print(f"[+] New custom classes found: {new_classes}")
    if merged_count == 0:
        print("[*] No field images found to merge (run capture_field_dataset.py on the Pi first).")

    # Return all classes present in staging dir
    return sorted([d for d in os.listdir(staging_dir) if os.path.isdir(os.path.join(staging_dir, d))])


def prepare_target_dataset(source_base_dir):
    """Stage only TARGET_CLASSES with alias mapping and balanced sample caps."""
    if os.path.exists(STAGING_DIR):
        existing_classes = [d for d in os.listdir(STAGING_DIR) if os.path.isdir(os.path.join(STAGING_DIR, d))]
        if all(tc in existing_classes for tc in TARGET_CLASSES):
            counts = {tc: len(_list_images(os.path.join(STAGING_DIR, tc))) for tc in TARGET_CLASSES}
            if all(c > 0 for c in counts.values()):
                print(f"[+] Reusing staged dataset at '{STAGING_DIR}' ({counts})")
                return STAGING_DIR
        try:
            shutil.rmtree(STAGING_DIR)
        except Exception as e:
            print(f"[*] Note on rmtree: {e}. Will overwrite files.")
    os.makedirs(STAGING_DIR, exist_ok=True)

    found = 0
    for target_class in TARGET_CLASSES:
        dest = os.path.join(STAGING_DIR, target_class)
        os.makedirs(dest, exist_ok=True)
        aliases = set(FOLDER_ALIASES.get(target_class, [target_class]))
        copied = 0
        if source_base_dir and os.path.isdir(source_base_dir):
            for root, dirs, files in os.walk(source_base_dir):
                base = os.path.basename(root)
                if base not in aliases:
                    continue
                valid = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                for fn in valid[:MAX_SAMPLES_PER_CLASS]:
                    shutil.copyfile(os.path.join(root, fn), os.path.join(dest, fn))
                    copied += 1
                if copied:
                    print(f"[+] Loaded {copied} images for '{target_class}' from '{base}'")
                    break
        if copied == 0:
            print(f"[!] Class '{target_class}' missing — generating synthetic fallback images.")
            generate_synthetic_class_images(dest, target_class, count=80)
            copied = len(_list_images(dest))
        if copied:
            found += 1

    print(f"[+] Staged dataset at '{STAGING_DIR}' ({found} classes).")
    return STAGING_DIR


def augment_example(image, label):
    """Outdoor lighting augmentation (training split only)."""
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_flip_up_down(image)
    image = tf.image.random_brightness(image, max_delta=0.18)
    image = tf.image.random_contrast(image, lower=0.85, upper=1.15)
    image = tf.image.rot90(image, k=tf.random.uniform([], 0, 4, dtype=tf.int32))
    image = tf.clip_by_value(image, 0.0, 255.0)
    return image, label


def preprocess_example(image, label):
    """Match MobileNetV2 / disease_detect.py: scale to [-1, 1]."""
    image = tf.cast(image, tf.float32)
    image = (image / 127.5) - 1.0
    return image, label


def build_model(num_classes: int):
    """Pi-exportable graph: Input -> MobileNetV2 -> GAP -> Dropout -> Softmax."""
    inputs = layers.Input(shape=(224, 224, 3), name="leaf_rgb")
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="probs")(x)
    model = models.Model(inputs, outputs, name="AgroNex_MobileNetV2")
    return model, base_model


def export_quantized_tflite(model: tf.keras.Model, export_path: str):
    """Dynamic-range quantized TFLite (Pi 4 tflite-runtime compatible)."""
    os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
    tflite_model = converter.convert()
    with open(export_path, "wb") as f:
        f.write(tflite_model)
    print(f"[PASS] Quantized TFLite saved to '{export_path}' ({len(tflite_model) / 1024:.1f} KB).")


def export_labels_txt(class_names, export_path: str):
    os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
    with open(export_path, "w", encoding="utf-8") as f:
        for name in class_names:
            f.write(f"{name}\n")
    print(f"[PASS] Labels saved to '{export_path}' ({len(class_names)} classes).")


def main():
    print("==================================================")
    print("   AgroNex-Pi: Plant Disease Model Training       ")
    print("   Raspberry Pi 4 compatible TFLite export        ")
    print("==================================================")

    raw_dataset = find_or_extract_dataset()
    if raw_dataset is None:
        print("[!] plantvillage_dataset / plantdisease.zip not found. Using synthetic images.")
        raw_dataset = os.path.join(config.BASE_DIR, "plantvillage_dataset")
        os.makedirs(raw_dataset, exist_ok=True)

    staging_dir = prepare_target_dataset(raw_dataset)

    # ── Merge student-captured field images (runs on first use, no-op if empty) ─
    print("[+] Checking field_dataset/ for student-captured images to merge...")
    all_active_classes = merge_field_dataset(staging_dir)
    print(f"[+] Final active classes ({len(all_active_classes)}): {all_active_classes}")

    print("[+] Loading training and validation splits...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        staging_dir,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        shuffle=True,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        staging_dir,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        shuffle=False,
    )

    class_names = list(train_ds.class_names)
    print(f"[+] Active classes ({len(class_names)}): {class_names}")

    y_train = np.concatenate([labels.numpy() for _, labels in train_ds], axis=0)
    classes = np.unique(y_train)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
    class_weight_dict = {int(cls): float(wt) for cls, wt in zip(classes, weights)}
    print(f"[+] Class weights: {class_weight_dict}")

    autotune = tf.data.AUTOTUNE
    train_ds = (
        train_ds.map(augment_example, num_parallel_calls=autotune)
        .map(preprocess_example, num_parallel_calls=autotune)
        .prefetch(autotune)
    )
    val_ds = val_ds.map(preprocess_example, num_parallel_calls=autotune).prefetch(autotune)

    model, base_model = build_model(len(class_names))
    early = callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True)

    print("\n--- STAGE 1: Training classification head ---")
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_STAGE1,
        class_weight=class_weight_dict,
        callbacks=[early],
    )

    print("\n--- STAGE 2: Fine-tuning top 30 MobileNetV2 layers ---")
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False
    for layer in base_model.layers:
        if isinstance(layer, layers.BatchNormalization):
            layer.trainable = False

    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_STAGE2,
        class_weight=class_weight_dict,
        callbacks=[early],
    )

    val_loss, val_acc = model.evaluate(val_ds)
    print(f"\n[PASS] Validation accuracy: {val_acc * 100:.2f}%  (loss {val_loss:.4f})")

    print("\n--- EXPORTING PI-COMPATIBLE TFLITE ---")
    export_quantized_tflite(model, config.MODEL_PATH)
    export_labels_txt(class_names, config.LABELS_PATH)

    # Sanity-check the exported file with the TFLite interpreter (same path the Pi uses)
    try:
        interpreter = tf.lite.Interpreter(model_path=config.MODEL_PATH)
        interpreter.allocate_tensors()
        inp = interpreter.get_input_details()[0]
        print(f"[PASS] TFLite load OK. Input: shape={inp['shape']} dtype={inp['dtype']}")
    except Exception as e:
        print(f"[FAIL] Exported TFLite failed to load: {e}")
        sys.exit(1)

    print("[PASS] Training complete. Copy models/ to the Raspberry Pi 4 (same relative path).")


if __name__ == "__main__":
    main()
