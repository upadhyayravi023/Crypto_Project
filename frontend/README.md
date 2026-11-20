# Next.js frontend on Vercel

This folder is the independent Vercel application. It calls the FastAPI backend through Next.js server-side route handlers.

## Deploy from GitHub

1. Import `upadhyayravi023/Crypto_Project` in Vercel.
2. Set **Root Directory** to `frontend` and keep the Next.js framework preset.
3. Add this Vercel project environment variable for Production (and Preview if needed):

   - `BACKEND_URL`: the public HTTPS URL of the Render backend, without a trailing slash.

4. Deploy. Vercel installs the dependencies from `package.json` and runs `npm run build`.

For local development, run `npm install` and `npm run dev` in this directory after setting `BACKEND_URL` in `frontend/.env.local`.

The backend credential is hardcoded as `DES-IOT-DEMO-ONLY-2026` in the frontend proxy and backend for this public academic demo, so no token environment variable is needed. Anyone who can read the repository can use it; do not use this setup for real or private data.
