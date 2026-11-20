import { proxy } from "../../../lib/backend";

export async function GET(request) {
  return proxy("api/events", { request });
}
