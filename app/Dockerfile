FROM python:3.7-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip

WORKDIR /app

COPY . ./

RUN pip install -r ./requirements.txt

EXPOSE 8501

VOLUME ["/app"]

ENTRYPOINT [ "streamlit", "run", "streamlit_app.py" ]