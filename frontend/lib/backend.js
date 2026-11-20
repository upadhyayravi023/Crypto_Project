import { NextResponse } from "next/server";

const TIMEOUT_MS = 120_000;

export async function proxy(path, { request, method = "GET", auth = true } = {}) {
  const baseUrl = process.env.BACKEND_URL?.replace(/\/$/, "");
  if (!baseUrl) {
    return NextResponse.json({ detail: "Set BACKEND_URL in the Vercel project environment." }, { status: 503 });
  }
  const target = new URL(`${baseUrl}/${path}`);
  if (request && method === "GET") {
    request.nextUrl.searchParams.forEach((value, key) => target.searchParams.set(key, value));
  }
  const headers = new Headers();
  if (auth) {
    const token = process.env.IOT_API_TOKEN;
    if (!token) return NextResponse.json({ detail: "IOT_API_TOKEN is not configured." }, { status: 503 });
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (method === "POST") headers.set("Content-Type", "application/json");
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const upstream = await fetch(target, {
      method,
      headers,
      body: method === "POST" ? await request.text() : undefined,
      cache: "no-store",
      signal: controller.signal,
    });
    const body = await upstream.text();
    return new NextResponse(body, {
      status: upstream.status,
      headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
    });
  } catch (error) {
    const message = error.name === "AbortError" ? "Backend request timed out." : "Backend service is not reachable.";
    return NextResponse.json({ detail: message }, { status: 502 });
  } finally {
    clearTimeout(timer);
  }
}
