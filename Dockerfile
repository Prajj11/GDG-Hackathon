FROM node:22-slim AS frontend-build
WORKDIR /frontend
ARG VITE_GUARDIAN_DISPLAY_NAME="Guardian workspace"
ENV VITE_GUARDIAN_DISPLAY_NAME=$VITE_GUARDIAN_DISPLAY_NAME
COPY package*.json ./
RUN npm ci
COPY index.html tsconfig*.json vite.config.ts ./
COPY src ./src
COPY public ./public
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HF_HOME=/app/backend/artifacts/hf-cache
COPY backend/requirements.txt backend/requirements-ml.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY app ./app
COPY digital_guardrails.db ./digital_guardrails.db
COPY --from=frontend-build /frontend/dist ./dist
ARG TRAIN_INDICBERT=false
RUN if [ "$TRAIN_INDICBERT" = "true" ]; then pip install --no-cache-dir -r backend/requirements-ml.txt && python -m backend.ml.train; fi
ENV DETECTOR=baseline MODEL_DIR=/app/backend/artifacts/indicbert DG_HOSTED=true
EXPOSE 8000
CMD ["python", "-m", "backend.serve"]
