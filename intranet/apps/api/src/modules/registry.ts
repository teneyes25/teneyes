export type ModuleDefinition = {
  key: string;
  path: string;
  title: string;
  description: string;
  roles: string[];
};

export const modules: ModuleDefinition[] = [
  { key: "notices", path: "/notices", title: "공지사항", description: "전사 공지와 필독 게시물을 관리합니다.", roles: ["employee"] },
  { key: "industry-news", path: "/industry-news", title: "산업뉴스", description: "업계 동향과 카드뉴스 발송 콘텐츠를 관리합니다.", roles: ["employee"] },
  { key: "qna", path: "/qna", title: "Q&A", description: "사내 질의응답과 FAQ를 운영합니다.", roles: ["employee"] },
  { key: "policies", path: "/policies", title: "규정", description: "인사, 보안, 복지 등 사내 규정을 제공합니다.", roles: ["employee"] },
  { key: "approvals", path: "/approvals", title: "전자결재", description: "품의, 휴가, 문서 승인 워크플로를 처리합니다.", roles: ["employee", "approver"] },
  { key: "documents", path: "/documents", title: "문서함", description: "권한 기반 문서 저장소와 다운로드 감사를 제공합니다.", roles: ["employee"] },
  { key: "org-chart", path: "/org-chart", title: "조직도", description: "부서, 직책, 연락처를 탐색합니다.", roles: ["employee"] },
  { key: "profile", path: "/profile", title: "내 프로필", description: "개인 정보와 알림 설정을 관리합니다.", roles: ["employee"] },
  { key: "product-catalog", path: "/product-catalog", title: "제품 카탈로그", description: "제품 자료, 가격표, 브로슈어를 확인합니다.", roles: ["employee", "dealer"] },
  { key: "dealers", path: "/dealers", title: "대리점", description: "대리점 정보와 영업 담당자를 관리합니다.", roles: ["sales", "admin"] },
  { key: "attendance", path: "/attendance", title: "근태", description: "출퇴근, 연차 잔여, 캘린더를 제공합니다.", roles: ["employee"] },
  { key: "admin", path: "/admin", title: "관리자", description: "사용자, 권한, 감사 로그, 시스템 설정을 관리합니다.", roles: ["admin"] }
];

export const moduleKeys = modules.map((module) => module.key);
