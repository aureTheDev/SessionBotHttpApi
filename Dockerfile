FROM python:latest

RUN apt update && apt install -y curl unzip && \
    curl -fsSL https://bun.sh/install | bash && \
    mv /root/.bun/bin/bun /usr/local/bin/bun && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .


RUN bun init --yes --cwd /app/session-messenger-utils
RUN bun add @session.js/client --cwd /app/session-messenger-utils

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]