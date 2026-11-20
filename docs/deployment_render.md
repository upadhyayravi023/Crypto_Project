# Vercel frontend and Render backend

The deployment has three pieces: a Next.js frontend in `frontend/` on Vercel, a FastAPI receiver in `backend/` on Render, and Render Postgres for readings and replay state. The Next.js server routes proxy requests to the backend, so the API token stays on the server and is never sent to browser JavaScript. The backend connects to an external MQTT-over-TLS broker.

## 1. Create a TLS MQTT broker

Create an [EMQX Cloud Serverless](https://www.emqx.com/en/cloud/serverless-mqtt) deployment and add a username/password client credential. Keep the deployment spend limit at zero for the free-quota demo. Record the hostname and credential in a password manager. EMQX Serverless uses MQTT over TLS on port `8883`; this project turns on TLS when `MQTT_TLS=true`. See the [EMQX connection guide](https://docs.emqx.com/en/cloud/latest/connect_to_deployments/deploy_mqtt_broker.html).

## 2. Deploy the backend on Render

### Blueprint method

1. In Render, choose **New > Blueprint** and connect `upadhyayravi023/Crypto_Project` on branch `main`.
2. Select the root `render.yaml` Blueprint. It creates the FastAPI web service and a free Postgres database.
3. Enter the requested secrets: `DES_KEY_B64`, `HMAC_KEY_B64`, `MQTT_HOST`, `MQTT_USERNAME`, and `MQTT_PASSWORD`.
4. Start the deploy. The backend health endpoint is `/health`.

### Manual service method

Create a Render **Web Service** from the GitHub repository, branch `main`, with the repository root as its Root Directory:

- Build command: `pip install -r backend/requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Create a Render Postgres database in the same region and set its internal connection string as `DATABASE_URL`. Add the variables in [`backend/README.md`](../backend/README.md).

Generate the two cryptographic keys locally:

```powershell
python -c "import base64,secrets; print('DES_KEY_B64='+base64.b64encode(secrets.token_bytes(8)).decode()); print('HMAC_KEY_B64='+base64.b64encode(secrets.token_bytes(32)).decode())"
```

Enter the values into Render's secret environment variables; do not put them in Git.

## 3. Deploy the frontend on Vercel

1. Import `upadhyayravi023/Crypto_Project` in Vercel.
2. Set **Root Directory** to `frontend`; use the Next.js preset.
3. Set the `BACKEND_URL` Production environment variable to the Render backend's public HTTPS URL, without a trailing slash.
4. Deploy. Vercel installs dependencies from `package.json` and runs `npm run build`.

For this public academic demo, the frontend proxy and backend share the hardcoded demo token `DES-IOT-DEMO-ONLY-2026`, so no API token environment variable is required. Anyone who can read the repository can use it; do not use this setup for real or private data.

## Free-tier limits

This setup is for a temporary showcase. Render free web services sleep after 15 minutes without inbound traffic; the first request after sleep can take about a minute. Render's free Postgres is limited to 1 GB and expires after 30 days. See [Render free plan limits](https://render.com/docs/free).

EMQX Serverless has a monthly free quota for session minutes, network traffic, and rule actions, then usage-based billing. Leave the spend limit at zero if offered by the account. Check the [EMQX plan limits](https://docs.emqx.com/en/cloud/latest/price/plans.html).

DES is obsolete. This deployment is an academic demonstration, not a production security service.
