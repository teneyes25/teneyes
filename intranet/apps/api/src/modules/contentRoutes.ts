import { Router } from "express";
import { z } from "zod";
import { query } from "../db/pool.js";
import { moduleKeys, modules } from "./registry.js";

const contentSchema = z.object({
  title: z.string().min(1),
  body: z.string().default(""),
  tags: z.array(z.string()).default([]),
  status: z.enum(["draft", "published", "archived"]).default("published")
});

const moduleSet = new Set(moduleKeys);

export const contentRouter = Router();

contentRouter.get("/modules", (_req, res) => {
  res.json({ modules });
});

contentRouter.get("/:moduleKey", async (req, res) => {
  const { moduleKey } = req.params;
  if (!moduleSet.has(moduleKey)) {
    return res.status(404).json({ message: "알 수 없는 모듈입니다." });
  }

  const { rows } = await query(
    `select id, module_key, title, body, tags, status, author_id, created_at, updated_at
     from module_items
     where module_key = $1
       and ($2::text is null or title ilike '%' || $2 || '%' or body ilike '%' || $2 || '%' or tags::text ilike '%' || $2 || '%')
     order by updated_at desc
     limit 100`,
    [moduleKey, typeof req.query.q === "string" ? req.query.q : null]
  );

  return res.json({ items: rows });
});

contentRouter.post("/:moduleKey", async (req, res) => {
  const { moduleKey } = req.params;
  if (!moduleSet.has(moduleKey)) {
    return res.status(404).json({ message: "알 수 없는 모듈입니다." });
  }

  const input = contentSchema.parse(req.body);
  const { rows } = await query(
    `insert into module_items (module_key, title, body, tags, status, author_id)
     values ($1, $2, $3, $4, $5, $6)
     returning id, module_key, title, body, tags, status, author_id, created_at, updated_at`,
    [moduleKey, input.title, input.body, input.tags, input.status, req.user?.id ?? "system"]
  );

  return res.status(201).json({ item: rows[0] });
});
