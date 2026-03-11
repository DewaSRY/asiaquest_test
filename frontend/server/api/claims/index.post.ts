import { proxyToBackend } from "../../utils/proxy";

export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  return proxyToBackend(event, "/claims", {
    method: "POST",
    body: JSON.stringify(body),
  });
});
