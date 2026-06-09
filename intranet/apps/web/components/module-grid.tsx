import { modules } from "../lib/modules";

export function ModuleGrid() {
  return (
    <section className="panel">
      <div className="section-heading">
        <p>전체 모듈</p>
        <span>공지부터 관리자까지 Phase 2 범위 포함</span>
      </div>
      <div className="grid">
        {modules.map((module) => (
          <article className="card" key={module.key}>
            <strong>{module.title}</strong>
            <p>{module.description}</p>
            <small>/{module.key}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
