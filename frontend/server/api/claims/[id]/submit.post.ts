import { proxyToBackend } from "../../../utils/proxy";

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id");
  return proxyToBackend(event, `/claims/${id}/submit`, {
    method: "POST",
  });
});
