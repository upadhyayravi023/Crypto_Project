import { proxy } from "../../../lib/backend";

export async function POST(request) {
  return proxy("api/benchmark", { request, method: "POST" });
}
