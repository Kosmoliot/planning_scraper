# Base Python (Debian Bookworm slim)
FROM python:3.11-slim

# Prevent interactive tzdata prompts and reduce image size
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for Chromium/Selenium
# Notes:
# - Use Debian package names (no Ubuntu-only packages)
# - chromium-driver provides /usr/lib/chromium/chromedriver
# - libgtk-3-0 is needed for recent Chromium builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    ca-certificates \
    curl \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libu2f-udev \
    xdg-utils \
 && rm -rf /var/lib/apt/lists/*

# Helpful envs for Selenium + Chromium
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER=/usr/lib/chromium/chromedriver \
    PATH="$PATH:/usr/lib/chromium"

# Workdir
WORKDIR /app

# Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# App source
COPY src/ ./src

# Expose (Railway will still inject $PORT)
EXPOSE 8080

# Important: bind Streamlit to $PORT that Railway provides
# Use a shell form so $PORT variable expands at runtime
CMD sh -c 'streamlit run src/main.py --server.port=${PORT:-8080} --server.address=0.0.0.0'
