const deployVersion = process.env.NEXT_PUBLIC_DEPLOY_VERSION ?? "local-dev";

function loginUrl() {
  return "/api/auth/signin?callbackUrl=https%3A%2F%2F192.168.0.6%2F";
}

export default function LoginPage() {
  return (
    <main className="login-page">
      <section className="login-shell">
        <div className="login-hero">
          <p className="eyebrow">Maejong SSO</p>
          <h1>인트라넷 통합 로그인</h1>
          <p>Keycloak SSO와 AD LDAP 그룹 기반 RBAC를 사용하는 최신 로그인 화면입니다.</p>
          <a className="login-primary" href={loginUrl()}>Keycloak SSO로 로그인</a>
          <p className="login-note">권한은 Keycloak 역할(employee, approver, sales, dealer, admin)에 따라 자동 적용됩니다.</p>
        </div>

        <aside className="login-panel">
          <div className="login-build">
            <span>빌드 확인</span>
            <strong>{deployVersion}</strong>
          </div>
          <h2>접속 정책</h2>
          <ul>
            <li>AD LDAP 사용자 동기화</li>
            <li>그룹 기반 RBAC 역할 매핑</li>
            <li>감사 로그 기반 로그인 추적 준비</li>
            <li>HTTPS 443 경유 접속</li>
          </ul>
          <div className="role-grid">
            {["employee", "approver", "sales", "dealer", "admin"].map((role) => (
              <span key={role}>{role}</span>
            ))}
          </div>
        </aside>
      </section>
    </main>
  );
}
