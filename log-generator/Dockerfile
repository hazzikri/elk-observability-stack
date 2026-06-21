FROM python:3.12-slim

WORKDIR /app
COPY generate_logs.py .

RUN useradd -r -s /bin/false loguser
USER loguser

CMD ["python", "generate_logs.py"]
