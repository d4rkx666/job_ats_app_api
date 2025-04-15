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

# Set environment variables
ENV DISPLAY=:99 \
    QT_QPA_PLATFORM=offscreen \
    PORT=8000

# Create start script
RUN echo '#!/bin/sh\n\
Xvfb :99 -screen 0 1024x768x24 &\n\
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT' > /start.sh && \
    chmod +x /start.sh

# Railway specifically looks for this command:
CMD ["/start.sh"]