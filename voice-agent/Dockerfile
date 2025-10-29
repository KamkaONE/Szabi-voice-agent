FROM python:3.12-slim

# System deps for audio & TLS
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Use a pinned req file (the one we agreed)
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# App code
COPY . /app

# Persisted memory lives here (capital L matters!)
VOLUME ["/opt/Livekit"]

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["python","-B","-u","app.py"]
