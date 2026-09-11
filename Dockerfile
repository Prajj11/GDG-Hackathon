FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HF_HOME=/app/backend/artifacts/hf-cache
COPY backend/requirements.txt backend/requirements-ml.txt ./backend/
RUN pip install --no-cache-dir 'torch>=2.6,<3' --index-url https://download.pytorch.org/whl/cpu && pip install --no-cache-dir -r backend/requirements-ml.txt
COPY backend ./backend
RUN python -m backend.ml.train
ENV DETECTOR=indicbert MODEL_DIR=/app/backend/artifacts/indicbert DG_HOSTED=true
EXPOSE 8000
CMD ["python", "-m", "backend.serve"]
