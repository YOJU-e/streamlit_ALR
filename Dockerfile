# 베이스 이미지 선택
FROM python:3.8-slim

# 시스템 패키지 설치
COPY packages.txt /tmp/packages.txt
RUN apt-get update && \
    apt-get install -y $(cat /tmp/packages.txt) && \
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
