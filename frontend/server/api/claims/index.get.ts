import { proxyToBackend } from "../../utils/proxy";

export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const queryString = new URLSearchParams(query as any).toString();
  const path = queryString ? `/claims?${queryString}` : "/claims";

  return proxyToBackend(event, path, {
    method: "GET",
  });
});
