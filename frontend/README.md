# Next.js frontend on Vercel

This folder is the independent Vercel application. It calls the protected FastAPI backend through Next.js server-side route handlers; the API token is never exposed to browser JavaScript.

## Deploy from GitHub

1. Import `upadhyayravi023/Crypto_Project` in Vercel.
2. Set **Root Directory** to `frontend` and keep the Next.js framework preset.
3. Add these Vercel project environment variables for Production (and Preview if needed):

   - `BACKEND_URL`: the public HTTPS URL of the Render backend, without a trailing slash.
   - `IOT_API_TOKEN`: the same random secret configured on the Render backend.

4. Deploy. Vercel installs the dependencies from `package.json` and runs `npm run build`.

For local development, run `npm install` and `npm run dev` in this directory after setting the same two variables in `frontend/.env.local`.
