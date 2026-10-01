FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --no-warn-script-location -r requirements.txt

COPY . .

# --workers=1 is strictly required to stay under 512MB RAM
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "1", "--threads", "1", "--timeout", "180", "app:app"]
