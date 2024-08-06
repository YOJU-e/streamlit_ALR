# this base image seems to be quite similar to the streamlit cloud environment
FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

# we need some build tools for installing additional python pip packages
RUN apt-get update \
    && apt-get install --yes \
    software-properties-common \
    build-essential \
    gcc \
    g++ \
    cmake \
    git \
    curl \
    python3-dev

# 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y wget unzip gnupg

# Chromium 저장소 추가 및 패키지 설치
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# 특정 버전의 chromium-driver 설치
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

WORKDIR /app

# 패키지 설치를 위한 packages.txt 복사 및 설치
COPY packages.txt packages.txt
RUN apt-get update && xargs -a packages.txt apt-get install --yes

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip setuptools wheel uv
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8501

HEALTHCHECK --interval=1m --timeout=20s \
    CMD curl --fail http://localhost:8501/_stcore/health

COPY . .

CMD ["streamlit", "run", "ALD_ex.py"]

# docker build --progress=plain --tag streamlit-selenium:latest .
# docker run -ti -p 8501:8501 --rm streamlit-selenium:latest
# docker run -ti -p 8501:8501 -v ${pwd}:/app --rm streamlit-selenium:latest
