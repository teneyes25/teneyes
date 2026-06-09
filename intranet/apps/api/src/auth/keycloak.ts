import type { NextFunction, Request, Response } from "express";
import { createRemoteJWKSet, jwtVerify } from "jose";
import { config } from "../config.js";

export type IntranetUser = {
  id: string;
  email: string;
  name: string;
  roles: string[];
  groups: string[];
};

declare global {
  namespace Express {
    interface Request {
      user?: IntranetUser;
    }
  }
}

const jwks = createRemoteJWKSet(new URL(`${config.KEYCLOAK_ISSUER}/protocol/openid-connect/certs`));

function realmRoles(payload: Record<string, unknown>) {
  const access = payload.realm_access as { roles?: string[] } | undefined;
  const resource = payload.resource_access as Record<string, { roles?: string[] }> | undefined;
  const clientRoles = resource?.[config.KEYCLOAK_AUDIENCE]?.roles ?? [];
  return [...new Set([...(access?.roles ?? []), ...clientRoles])];
}

function userFromPayload(payload: Record<string, unknown>): IntranetUser {
  return {
    id: String(payload.sub ?? "dev-user"),
    email: String(payload.email ?? "dev@maejong.local"),
    name: String(payload.name ?? payload.preferred_username ?? "개발 사용자"),
    roles: realmRoles(payload),
    groups: Array.isArray(payload.groups) ? payload.groups.map(String) : []
  };
}

export async function requireAuth(req: Request, res: Response, next: NextFunction) {
  const auth = req.header("authorization");

  if (!auth?.startsWith("Bearer ")) {
    if (!config.AUTH_REQUIRED) {
      req.user = {
        id: "dev-user",
        email: "dev@maejong.local",
        name: "개발 사용자",
        roles: ["admin", "employee"],
        groups: ["/임직원", "/전산관리자"]
      };
      return next();
    }

    return res.status(401).json({ message: "인증 토큰이 필요합니다." });
  }

  try {
    const { payload } = await jwtVerify(auth.slice("Bearer ".length), jwks, {
      issuer: config.KEYCLOAK_ISSUER,
      audience: config.KEYCLOAK_AUDIENCE
    });
    req.user = userFromPayload(payload);
    return next();
  } catch {
    return res.status(401).json({ message: "유효하지 않은 인증 토큰입니다." });
  }
}

export function requireRole(...allowedRoles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    const roles = req.user?.roles ?? [];
    if (allowedRoles.some((role) => roles.includes(role))) {
      return next();
    }

    return res.status(403).json({ message: "권한이 없습니다.", requiredRoles: allowedRoles });
  };
}
