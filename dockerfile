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

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables for headless operation
ENV DISPLAY=:99 \
    QT_QPA_PLATFORM=offscreen

# Run with Xvfb and Uvicorn
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 && py -m app.main"]
