# Free deployment

The free path uses GitHub Pages for the React frontend and Render's free web
service for the FastAPI API. Render is configured with the TF-IDF fallback
detector so it does not need the memory required by IndicBERTv2. The IndicBERT
detector remains available by setting `DETECTOR=indicbert` and building a larger
runtime with trained artifacts.

## GitHub Pages

1. In the GitHub repository settings, open **Pages** and set the source to
   **GitHub Actions**.
2. Add the repository variable `VITE_API_URL` with the final Render API URL,
   ending in `/api` (for example, `https://your-api.onrender.com/api`).
3. Push to `main`. The workflow in `.github/workflows/deploy-pages.yml` builds
   and publishes the frontend at `https://<owner>.github.io/GDG-Hackathon/`.

## Render

1. In Render, choose **New → Blueprint** and select this repository.
2. Confirm the `digital-guardrails-api` service from `render.yaml`.
3. Set `CORS_ORIGINS` to the GitHub Pages URL, then deploy.
4. Copy the Render service URL into the GitHub variable `VITE_API_URL` and push
   once more to rebuild the frontend against the API.

The free Render service may sleep when idle, so the first request can take a
short while. SQLite data is suitable for a demo; use PostgreSQL and IndicBERTv2
on a larger production runtime.
