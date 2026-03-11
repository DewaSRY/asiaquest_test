import { proxyToBackend } from "../../utils/proxy";

export default defineEventHandler(async (event) => {
  return proxyToBackend(event, "/auth/me", {
    method: "GET",
  });
});
