# 베이스 이미지 선택
FROM python:3.8-slim

# 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y wget unzip

# 특정 버전의 chromium-browser와 chromium-driver 설치
RUN apt-get install -y chromium-browser=90.0.4430.93-0ubuntu0.20.04.1 && \
    apt-get install -y chromium-chromedriver=90.0.4430.93-0ubuntu0.20.04.1 && \
    rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# 환경 변수 설정
ENV PATH="/usr/lib/chromium:${PATH}"
ENV CHROMIUM_BIN="/usr/bin/chromium"

# 앱 파일 복사 및 작업 디렉토리 설정
COPY . /app
WORKDIR /app

# 스트림릿 앱 실행
CMD ["streamlit", "run", "ALD_ex.py"]
