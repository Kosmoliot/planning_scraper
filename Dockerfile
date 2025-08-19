FROM python:3.11-slim

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# System deps for Chromium/Selenium + useful fonts/libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    wget \
    curl \
    unzip \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libu2f-udev \
    xdg-utils \
    libayatana-appindicator3-1 \
 && rm -rf /var/lib/apt/lists/*

# Headless Chromium environment
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver
ENV PATH="$PATH:/usr/bin"

# App setup
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src

# Streamlit on Railway-friendly port
EXPOSE 8080
CMD ["streamlit", "run", "src/main.py", "--server.port=8080", "--server.address=0.0.0.0"]
