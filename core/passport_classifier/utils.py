from PIL import Image
import numpy as np
import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "passport_model.keras")

model = tf.keras.models.load_model(model_path)

class_indices = {'back': 0, 'face': 1, 'front': 2}
class_names = {v: k for k, v in class_indices.items()}

def predict_passport_photo(image_file, expected_type: str = None):
    try:
        img = Image.open(image_file)
    except Exception as e:
        print(f"❌ Ошибка при открытии изображения: {e}")
        return False

    img = img.convert('RGB')
    img = img.resize((224, 224))

    img_array = np.array(img) / 255.0
    if img_array.shape != (224, 224, 3):
        print(f"❌ Неверная форма изображения: {img_array.shape}")
        return False

    img_array = img_array.reshape((1, 224, 224, 3))

    prediction = model.predict(img_array)[0]
    predicted_class = int(np.argmax(prediction))
    predicted_label = class_names[predicted_class]

    print(f"🔍 Prediction probabilities: {prediction}")
    print(f"✅ Predicted class: {predicted_label}")

    if expected_type:
        expected_class = class_indices.get(expected_type, -1)
        print(f"🎯 Expected class: {expected_type} ({expected_class})")
        return predicted_class == expected_class

    return predicted_label
