export function PhaseTwoPanel() {
  return (
    <section className="panel">
      <div className="section-heading">
        <p>Phase 2 배포 준비</p>
        <span>SSO, HTTPS, SMTP, 감사, RBAC</span>
      </div>
      <ul className="checklist">
        <li>Keycloak AD LDAP 사용자 연동 및 그룹→역할 매핑</li>
        <li>Nginx 443 HTTPS 리버스 프록시와 HSTS 적용</li>
        <li>SMTP 카드뉴스 발송과 Maejong AI 요약</li>
        <li>로그인, 다운로드, 결재, 근태 감사 로그</li>
      </ul>
    </section>
  );
}
