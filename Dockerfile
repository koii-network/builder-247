FROM python:3.12-slim

RUN useradd -m -s /bin/bash testuser

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chown -R testuser:testuser /app

USER testuser

CMD ["python3", "-m", "pytest", "tests/", "-v"]
