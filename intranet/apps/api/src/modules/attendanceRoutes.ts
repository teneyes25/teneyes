import { Router } from "express";
import { z } from "zod";
import { query } from "../db/pool.js";
import { writeAuditLog } from "../services/auditLog.js";

export const attendanceRouter = Router();

const clockSchema = z.object({
  memo: z.string().optional()
});

attendanceRouter.post("/clock-in", async (req, res) => {
  const input = clockSchema.parse(req.body);
  const { rows } = await query(
    `insert into attendance_events (user_id, event_type, memo)
     values ($1, 'clock_in', $2)
     returning id, user_id, event_type, event_at, memo`,
    [req.user?.id, input.memo ?? null]
  );
  await writeAuditLog(req, "attendance.clock_in", "attendance_event", rows[0].id);
  return res.status(201).json({ event: rows[0] });
});

attendanceRouter.post("/clock-out", async (req, res) => {
  const input = clockSchema.parse(req.body);
  const { rows } = await query(
    `insert into attendance_events (user_id, event_type, memo)
     values ($1, 'clock_out', $2)
     returning id, user_id, event_type, event_at, memo`,
    [req.user?.id, input.memo ?? null]
  );
  await writeAuditLog(req, "attendance.clock_out", "attendance_event", rows[0].id);
  return res.status(201).json({ event: rows[0] });
});

attendanceRouter.get("/leave-balance", async (req, res) => {
  const { rows } = await query(
    `select user_id, year, annual_total, annual_used, annual_total - annual_used as annual_remaining
     from leave_balances
     where user_id = $1 and year = extract(year from now())::int`,
    [req.user?.id]
  );

  return res.json({
    balance: rows[0] ?? {
      user_id: req.user?.id,
      year: new Date().getFullYear(),
      annual_total: 15,
      annual_used: 0,
      annual_remaining: 15
    }
  });
});

attendanceRouter.get("/calendar", async (req, res) => {
  const { rows } = await query(
    `select id, user_id, event_type, event_at, memo
     from attendance_events
     where user_id = $1
       and event_at >= coalesce($2::timestamptz, date_trunc('month', now()))
       and event_at < coalesce($3::timestamptz, date_trunc('month', now()) + interval '1 month')
     order by event_at asc`,
    [
      req.user?.id,
      typeof req.query.from === "string" ? req.query.from : null,
      typeof req.query.to === "string" ? req.query.to : null
    ]
  );

  return res.json({ events: rows });
});
