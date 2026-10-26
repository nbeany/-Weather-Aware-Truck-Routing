# Single image for Render: builds the React app, then serves it and the Django API
# from one Gunicorn process (the frontend calls /api on the same origin).

FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Empty base URL: the browser calls /api on the same host.
ENV VITE_API_BASE_URL=""
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FRONTEND_DIST=/app/frontend/dist
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend /app/frontend/dist /app/frontend/dist
# Write .gz and .br copies next to each file so WhiteNoise can send them compressed.
RUN python -m whitenoise.compress /app/frontend/dist
RUN useradd --create-home app
USER app
# gunicorn.conf.py binds to $PORT, which Render sets.
CMD ["gunicorn", "-c", "gunicorn.conf.py", "config.wsgi:application"]
