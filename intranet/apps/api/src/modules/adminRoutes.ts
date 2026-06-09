import { Router } from "express";
import { query } from "../db/pool.js";
import { requireRole } from "../auth/keycloak.js";

export const adminRouter = Router();

adminRouter.use(requireRole("admin"));

adminRouter.get("/audit-logs", async (req, res) => {
  const { rows } = await query(
    `select id, actor_id, actor_email, action, target_type, target_id, ip_address, user_agent, metadata, created_at
     from audit_logs
     where ($1::text is null or action = $1)
     order by created_at desc
     limit 200`,
    [typeof req.query.action === "string" ? req.query.action : null]
  );

  return res.json({ auditLogs: rows });
});

adminRouter.get("/rbac-map", (_req, res) => {
  res.json({
    keycloakRoles: ["employee", "approver", "sales", "dealer", "admin"],
    activeDirectoryGroups: {
      "CN=Intranet-Employees,OU=Groups,DC=maejong,DC=local": "employee",
      "CN=Intranet-Approvers,OU=Groups,DC=maejong,DC=local": "approver",
      "CN=Intranet-Sales,OU=Groups,DC=maejong,DC=local": "sales",
      "CN=Intranet-Dealers,OU=Groups,DC=maejong,DC=local": "dealer",
      "CN=Intranet-Admins,OU=Groups,DC=maejong,DC=local": "admin"
    }
  });
});
