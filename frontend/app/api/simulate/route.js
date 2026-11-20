import { proxy } from "../../../lib/backend";

export async function POST(request) {
  return proxy("api/simulate", { request, method: "POST" });
}
