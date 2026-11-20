import { proxy } from "../../../lib/backend";

export async function GET() {
  return proxy("health", { auth: false });
}
