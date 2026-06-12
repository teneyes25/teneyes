import { AttendancePanel } from "../components/attendance-panel";
import { DocumentPanel } from "../components/document-panel";
import { IndustryNewsBoard } from "../components/industry-news-board";
import { MaejongChatWidget } from "../components/maejong-chat-widget";
import { ModuleGrid } from "../components/module-grid";
import { PhaseTwoPanel } from "../components/phase-two-panel";

export default function Home() {
  const deployVersion = process.env.NEXT_PUBLIC_DEPLOY_VERSION ?? "local-dev";

  return (
    <main>
      <section className="hero">
        <div>
          <p className="eyebrow">Maejong Intranet</p>
          <h1>인트라넷 홈페이지</h1>
          <p>오늘의 업계뉴스, 전자결재, 문서, 근태, 메종이 AI 상담을 한 화면에서 확인합니다.</p>
        </div>
        <div className="hero-badge">
          <span>운영 상태</span>
          <strong>HTTPS + SSO + AI Agent</strong>
        </div>
      </section>

      <section className="build-proof" aria-label="현재 배포 빌드 확인">
        <span>빌드 확인</span>
        <strong>{deployVersion}</strong>
        <p>이 값이 보이면 현재 브라우저 화면은 방금 빌드된 Web 컨테이너 산출물입니다.</p>
      </section>

      <section className="dashboard-kpis" aria-label="인트라넷 핵심 현황">
        <article>
          <span>오늘 업계뉴스</span>
          <strong>자동 수집</strong>
          <p>침구/매트리스 키워드 중요도 기준</p>
        </article>
        <article>
          <span>전자결재</span>
          <strong>기안 지원</strong>
          <p>메종이가 목적·배경·리스크를 점검</p>
        </article>
        <article>
          <span>문서/자료</span>
          <strong>학습 가능</strong>
          <p>파일·캡처 업로드로 메종이 지식 확장</p>
        </article>
        <article>
          <span>보안 접속</span>
          <strong>443 HTTPS</strong>
          <p>Keycloak RBAC와 감사 로그 준비</p>
        </article>
      </section>

      <div className="dashboard-layout">
        <div className="dashboard-main">
          <IndustryNewsBoard />
          <ModuleGrid />
        </div>
        <aside className="dashboard-side" aria-label="빠른 업무 현황">
          <AttendancePanel />
          <DocumentPanel />
          <PhaseTwoPanel />
        </aside>
      </div>

      <MaejongChatWidget />
    </main>
  );
}
