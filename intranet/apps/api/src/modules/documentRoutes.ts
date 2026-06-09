import { randomUUID } from "node:crypto";
import { Router } from "express";
import multer from "multer";
import { z } from "zod";
import { config } from "../config.js";
import { query } from "../db/pool.js";
import { writeAuditLog } from "../services/auditLog.js";
import { ensureDocumentBucket, minio } from "../services/storage.js";

export const documentRouter = Router();
const upload = multer({ storage: multer.memoryStorage() });

const documentMetaSchema = z.object({
  title: z.string().min(1),
  folderId: z.string().uuid().optional(),
  tags: z.string().optional(),
  allowedRoles: z.string().optional()
});

function roleFilter(roles: string[]) {
  return roles.length ? roles : ["employee"];
}

documentRouter.get("/", async (req, res) => {
  const userRoles = roleFilter(req.user?.roles ?? []);
  const tag = typeof req.query.tag === "string" ? req.query.tag : null;
  const q = typeof req.query.q === "string" ? req.query.q : null;
  const folderId = typeof req.query.folderId === "string" ? req.query.folderId : null;

  const { rows } = await query(
    `select id, title, file_name, content_type, size_bytes, tags, folder_id, allowed_roles, created_at
     from documents
     where ($1::text is null or title ilike '%' || $1 || '%' or tags::text ilike '%' || $1 || '%')
       and ($2::text is null or $2 = any(tags))
       and ($3::uuid is null or folder_id = $3)
       and allowed_roles && $4::text[]
     order by created_at desc
     limit 100`,
    [q, tag, folderId, userRoles]
  );

  return res.json({ documents: rows });
});

documentRouter.post("/", upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: "업로드할 파일이 필요합니다." });
  }

  const input = documentMetaSchema.parse(req.body);
  const objectKey = `${randomUUID()}-${req.file.originalname}`;
  await ensureDocumentBucket();
  await minio.putObject(config.MINIO_BUCKET, objectKey, req.file.buffer, req.file.size, {
    "content-type": req.file.mimetype
  });

  const tags = input.tags?.split(",").map((tag) => tag.trim()).filter(Boolean) ?? [];
  const allowedRoles = input.allowedRoles?.split(",").map((role) => role.trim()).filter(Boolean) ?? ["employee"];
  const { rows } = await query(
    `insert into documents (title, file_name, object_key, content_type, size_bytes, tags, folder_id, allowed_roles, created_by)
     values ($1, $2, $3, $4, $5, $6, $7, $8, $9)
     returning id, title, file_name, content_type, size_bytes, tags, folder_id, allowed_roles, created_at`,
    [
      input.title,
      req.file.originalname,
      objectKey,
      req.file.mimetype,
      req.file.size,
      tags,
      input.folderId ?? null,
      allowedRoles,
      req.user?.id
    ]
  );

  await writeAuditLog(req, "document.upload", "document", rows[0].id);
  return res.status(201).json({ document: rows[0] });
});

documentRouter.get("/:documentId/download", async (req, res) => {
  const { rows } = await query(
    `select id, title, file_name, object_key, content_type, allowed_roles
     from documents
     where id = $1 and allowed_roles && $2::text[]`,
    [req.params.documentId, roleFilter(req.user?.roles ?? [])]
  );

  const document = rows[0];
  if (!document) {
    return res.status(404).json({ message: "문서를 찾을 수 없거나 권한이 없습니다." });
  }

  await writeAuditLog(req, "download", "document", document.id, { fileName: document.file_name });
  const stream = await minio.getObject(config.MINIO_BUCKET, document.object_key);
  res.setHeader("content-type", document.content_type);
  res.setHeader("content-disposition", `attachment; filename="${encodeURIComponent(document.file_name)}"`);
  stream.pipe(res);
});
