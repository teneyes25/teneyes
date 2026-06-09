export function DocumentPanel() {
  return (
    <section className="panel">
      <div className="section-heading">
        <p>문서 저장소</p>
        <span>검색, 태그, 폴더 권한, 다운로드 감사</span>
      </div>
      <div className="search-row">
        <input aria-label="문서 검색어" placeholder="문서명, 태그, 본문 검색" />
        <button>검색</button>
      </div>
      <div className="doc-list">
        <div>
          <strong>영업 브로슈어</strong>
          <span>#제품 #대리점 · employee, dealer</span>
        </div>
        <div>
          <strong>보안 정책</strong>
          <span>#규정 #보안 · employee</span>
        </div>
      </div>
    </section>
  );
}
