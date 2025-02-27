# 1️⃣ Python 3.12 slim 이미지 사용 (가벼운 버전)
FROM python:3.12-slim

# 2️⃣ 크롤링용 사용자 생성
RUN useradd -m crawler

# 3️⃣ 작업 디렉토리 설정
WORKDIR /app

# 4️⃣ 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    curl unzip \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ 애플리케이션 코드 복사
COPY . .

# 7️⃣ 환경 변수 설정
ENV PATH="/usr/lib/chromium/:/usr/bin/chromium:${PATH}"

# 8️⃣ 실행 명령어 설정
CMD ["python", "app.py"]
