import { AttendancePanel } from "../components/attendance-panel";
import { DocumentPanel } from "../components/document-panel";
import { IndustryNewsBoard } from "../components/industry-news-board";
import { MaejongChatWidget } from "../components/maejong-chat-widget";
import { ModuleGrid } from "../components/module-grid";
import { PhaseTwoPanel } from "../components/phase-two-panel";

export default function Home() {
  return (
    <main>
      <section className="hero">
        <div>
          <p className="eyebrow">Maejong Intranet</p>
          <h1>Phase 2 배포 준비 대시보드</h1>
          <p>Next.js, Express, PostgreSQL, MinIO, Keycloak, Nginx 구성을 저장소에 영속화했습니다.</p>
        </div>
        <div className="hero-badge">
          <span>SSO</span>
          <strong>AD LDAP + Keycloak RBAC</strong>
        </div>
      </section>
      <IndustryNewsBoard />
      <ModuleGrid />
      <div className="split">
        <AttendancePanel />
        <DocumentPanel />
      </div>
      <PhaseTwoPanel />
      <MaejongChatWidget />
    </main>
  );
}
