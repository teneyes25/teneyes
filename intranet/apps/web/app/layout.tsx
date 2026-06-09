import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "매종 인트라넷",
  description: "Phase 2 SSO, 문서, 근태, 결재 통합 인트라넷"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
