FROM python:3.10-slim

# Install light OpenCV C++ dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Disable pip cache to save RAM during build
RUN pip install --no-cache-dir --no-warn-script-location -r requirements.txt

COPY . .

# --workers=1 to prevent duplicating ML models in RAM
# --threads=2 for concurrency without multiplying model size
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "1", "--threads", "2", "--timeout", "180", "app:app"]
