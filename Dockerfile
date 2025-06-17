# Gunakan image Python slim untuk efisiensi
FROM python:3.10-slim

# Install OS dependencies
RUN apt-get update && apt-get install -y build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port Flask
EXPOSE 5001

# Jalankan Gunicorn saat container start
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "api:app"]
