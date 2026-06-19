import { Router } from "express";
import { z } from "zod";
import { query } from "../db/pool.js";
import { writeAuditLog } from "../services/auditLog.js";

export const approvalRouter = Router();

const approvalSchema = z.object({
  title: z.string().min(1),
  body: z.string().min(1),
  approverId: z.string().min(1)
});

approvalRouter.get("/", async (_req, res) => {
  const { rows } = await query(
    `select id, title, body, requester_id, approver_id, status, created_at, updated_at
     from approvals
     order by updated_at desc
     limit 100`
  );

  return res.json({ approvals: rows });
});

approvalRouter.post("/", async (req, res) => {
  const input = approvalSchema.parse(req.body);
  const { rows } = await query(
    `insert into approvals (title, body, requester_id, approver_id, status)
     values ($1, $2, $3, $4, 'pending')
     returning id, title, body, requester_id, approver_id, status, created_at, updated_at`,
    [input.title, input.body, req.user?.id, input.approverId]
  );

  await writeAuditLog(req, "approval.created", "approval", rows[0].id);
  return res.status(201).json({ approval: rows[0] });
});

approvalRouter.post("/:approvalId/:action", async (req, res) => {
  if (!["approve", "reject"].includes(req.params.action)) {
    return res.status(400).json({ message: "지원하지 않는 결재 액션입니다." });
  }

  const status = req.params.action === "approve" ? "approved" : "rejected";
  const { rows } = await query(
    `update approvals
     set status = $1, updated_at = now()
     where id = $2
     returning id, title, body, requester_id, approver_id, status, created_at, updated_at`,
    [status, req.params.approvalId]
  );

  if (!rows[0]) {
    return res.status(404).json({ message: "결재 문서를 찾을 수 없습니다." });
  }

  await writeAuditLog(req, status === "approved" ? "approval.approved" : "approval.rejected", "approval", rows[0].id);
  return res.json({ approval: rows[0] });
});
