# 베이스 이미지 설정
FROM python:3.11-slim-bullseye

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

# 필요한 패키지 및 툴 설치
RUN apt-get update && apt-get install --yes \
    software-properties-common \
    build-essential \
    gcc \
    g++ \
    cmake \
    git \
    curl \
    python3-dev \
    wget \
    unzip \
    gnupg

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

# 작업 디렉토리 설정
WORKDIR /app

# 패키지 설치를 위한 packages.txt 복사 및 설치
COPY packages.txt /tmp/packages.txt
RUN apt-get update && \
    while read package; do apt-get install -y "$package"; done < /tmp/packages.txt

# Python 패키지 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 포트 노출
EXPOSE 8501

# 헬스체크 설정
HEALTHCHECK --interval=1m --timeout=20s \
    CMD curl --fail http://localhost:8501/_stcore/health

# 어플리케이션 복사
COPY . .

# 어플리케이션 실행 명령어
CMD ["streamlit", "run", "ALD_ex.py"]

# Docker 명령어 예시
# docker build --progress=plain --tag streamlit-selenium:latest .
# docker run -ti -p 8501:8501 --rm streamlit-selenium:latest
# docker run -ti -p 8501:8501 -v ${pwd}:/app --rm streamlit-selenium:latest
