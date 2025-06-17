# Gunakan base image Python versi ringan
FROM python:3.10-slim

# Install dependencies sistem untuk Pillow dan TensorFlow
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set direktori kerja dalam container
WORKDIR /app

# Copy semua file dari folder lokal ke dalam container
COPY . .

# Install pip dan pustaka Python yang dibutuhkan
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# Install Python libraries (TensorFlow, Pillow, Numpy, dll)
RUN pip install tensorflow==2.11.0 pillow numpy flask gunicorn

# Buka port untuk Flask API
EXPOSE 5001

# Perintah untuk menjalankan aplikasi menggunakan Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "api:app"]

