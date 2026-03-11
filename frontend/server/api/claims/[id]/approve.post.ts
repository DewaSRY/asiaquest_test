import { proxyToBackend } from "../../../utils/proxy";

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id");
  const body = await readBody(event);
  return proxyToBackend(event, `/claims/${id}/approve`, {
    method: "POST",
    body: JSON.stringify(body),
  });
});
