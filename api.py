from flask import Flask, request, jsonify
from keras.models import load_model  # Keras 3.x import
import numpy as np
from PIL import Image
import io
import os

DISEASE_MAP = {
    "0": "Actinic keratosis",
    "1": "Benign keratosis",
    "2": "Dermatofibroma",
    "3": "Melanocytic nevus",
    "4": "Melanoma",
    "5": "Squamous cell carcinoma",
    "6": "Tinea Ringworm Candidiasis",
    "7": "Vascular lesion"
}

RECOMMENDATIONS = {
    "Actinic keratosis": "Perlu evaluasi dokter kulit. Dapat diobati dengan krioterapi atau resep obat topikal.",
    "Benign keratosis": "Tidak memerlukan perawatan kecuali mengganggu secara kosmetik.",
    "Dermatofibroma": "Tidak memerlukan perawatan kecuali menyebabkan gejala.",
    "Melanocytic nevus": "Pantau perubahan bentuk, warna, atau ukuran. Konsultasi jika ada perubahan.",
    "Melanoma": "Segera konsultasi dengan dokter kulit untuk evaluasi lebih lanjut dan penanganan.",
    "Squamous cell carcinoma": "Perlu penanganan medis segera dengan operasi atau terapi lainnya.",
    "Tinea Ringworm Candidiasis": "Dapat diobati dengan obat antijamur topikal atau oral.",
    "Vascular lesion": "Evaluasi oleh dokter untuk menentukan perlu tidaknya perawatan."
}

app = Flask(__name__)

# Get the directory where api.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "model_klasifikasi.h5")

# Verify file exists
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

# Load model
model = load_model(model_path)

# # Load your Keras model
# model_dir = os.path.dirname(os.path.abspath(__file__))
# model_path = os.path.join(model_dir, "model_klasifikasi.h5")

# # Verify model exists
# if not os.path.exists(model_path):
#     raise FileNotFoundError(f"Model file not found at {model_path}")

# Define allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image):
    """Resize, normalize, etc. (adjust based on your model's requirements)"""
    img = Image.open(io.BytesIO(image))
    
    # Convert to RGB if image has alpha channel
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    img = img.resize((224, 224))  # Example size, adjust accordingly
    img_array = np.array(img) / 255.0  # Normalize
    
    # Ensure we have 3 channels (some grayscale images might have only 1)
    if len(img_array.shape) == 2:  # Grayscale
        img_array = np.stack((img_array,)*3, axis=-1)
    elif img_array.shape[2] == 4:  # RGBA
        img_array = img_array[..., :3]  # Drop alpha channel
    
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read and preprocess image
            img_bytes = file.read()
            processed_img = preprocess_image(img_bytes)

            # Run prediction
            prediction = model.predict(processed_img)
            class_id = str(np.argmax(prediction[0]))  # Get the class with highest probability
            probability = float(np.max(prediction[0]))  # Get the highest probability
            
            # Determine if malignant based on class_id
            is_malignant = class_id in ['0', '4', '5']  # Actinic keratosis, Melanoma, Squamous cell carcinoma

            disease_name = DISEASE_MAP.get(class_id, "Unknown")
            
            return jsonify({
                "classId": class_id,
                "probability": probability,
                "isMalignant": is_malignant,
                "diseaseName": disease_name,
                "features": {
                    "asymmetry": "low",
                    "border": "irregular",
                    "color": "mixed",
                    "diameter": "medium",
                    "evolution": "stable"
                },
                "recommendation": RECOMMENDATIONS.get(disease_name, "Consult a dermatologist")
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Different port than Node.js