FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    wkhtmltopdf \
    xvfb \
    libxrender1 \
    libjpeg62-turbo \
    fontconfig \
    xfonts-75dpi \
    xfonts-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables for headless operation
ENV DISPLAY=:99 \
    QT_QPA_PLATFORM=offscreen

# Start Xvfb and Uvicorn with your settings
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"]