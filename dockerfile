FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y \
    wkhtmltopdf \
    xvfb \
    libxrender1 \
    libjpeg62-turbo \
    fontconfig \
    xfonts-75dpi \
    xfonts-base

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENV DISPLAY=:99
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & uvicorn app.main:app --host 0.0.0.0 --port $PORT"]