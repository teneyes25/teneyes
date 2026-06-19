import { Router } from "express";
import { config } from "../config.js";

export const authRouter = Router();

function safeRedirectUri(value: unknown) {
  if (typeof value !== "string") {
    return "https://192.168.0.6/";
  }

  try {
    const url = new URL(value);
    if (["https://192.168.0.6", "http://192.168.0.6:3000", "https://localhost", "http://localhost:3000"].includes(url.origin)) {
      return url.toString();
    }
  } catch {
    // Fall through to default.
  }

  return "https://192.168.0.6/";
}

authRouter.get("/signin", (req, res) => {
  const redirectUri = safeRedirectUri(req.query.callbackUrl);
  const params = new URLSearchParams({
    client_id: "intranet-web",
    redirect_uri: redirectUri,
    response_type: "code",
    scope: "openid profile email"
  });

  res.redirect(302, `${config.KEYCLOAK_PUBLIC_ISSUER}/protocol/openid-connect/auth?${params.toString()}`);
});
