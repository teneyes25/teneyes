import nodemailer from "nodemailer";
import { config } from "../config.js";

const transporter = nodemailer.createTransport({
  host: config.SMTP_HOST,
  port: config.SMTP_PORT,
  secure: config.SMTP_PORT === 465
});

export async function sendCardNewsEmail(to: string[], subject: string, html: string) {
  return transporter.sendMail({
    from: config.SMTP_FROM,
    to,
    subject,
    html
  });
}
