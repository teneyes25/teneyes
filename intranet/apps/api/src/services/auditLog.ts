import type { Request } from "express";
import { query } from "../db/pool.js";

export type AuditAction =
  | "login"
  | "download"
  | "approval.created"
  | "approval.approved"
  | "approval.rejected"
  | "attendance.clock_in"
  | "attendance.clock_out"
  | "document.upload";

export async function writeAuditLog(req: Request, action: AuditAction, targetType: string, targetId?: string, metadata: Record<string, unknown> = {}) {
  const actor = req.user;

  await query(
    `insert into audit_logs (actor_id, actor_email, action, target_type, target_id, ip_address, user_agent, metadata)
     values ($1, $2, $3, $4, $5, $6, $7, $8)`,
    [
      actor?.id ?? "anonymous",
      actor?.email ?? "anonymous",
      action,
      targetType,
      targetId ?? null,
      req.ip,
      req.header("user-agent") ?? null,
      metadata
    ]
  );
}
