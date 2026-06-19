# Phase 2 구현 메모

## AD LDAP + Keycloak SSO

- Keycloak realm: `maejong-intranet`
- API audience: `intranet-api`
- Web client: `intranet-web`
- LDAP provider: `maejong-ad-ldap`
- 운영 환경에서는 `connectionUrl`, `usersDn`, `bindDn`, `KC_LDAP_BIND_CREDENTIAL`을 실제 AD 값으로 교체합니다.

## AD 그룹과 Keycloak 역할

| AD 그룹 DN | Keycloak 역할 |
|---|---|
| `CN=Intranet-Employees,OU=Groups,DC=maejong,DC=local` | `employee` |
| `CN=Intranet-Approvers,OU=Groups,DC=maejong,DC=local` | `approver` |
| `CN=Intranet-Sales,OU=Groups,DC=maejong,DC=local` | `sales` |
| `CN=Intranet-Dealers,OU=Groups,DC=maejong,DC=local` | `dealer` |
| `CN=Intranet-Admins,OU=Groups,DC=maejong,DC=local` | `admin` |

## 감사 로그 범위

- `download`: 문서 다운로드
- `approval.created`, `approval.approved`, `approval.rejected`: 전자결재 처리
- `attendance.clock_in`, `attendance.clock_out`: 근태 기록
- `document.upload`: 문서 등록
- `login`: Keycloak 이벤트 리스너 또는 API 로그인 콜백 확장 시 같은 테이블에 적재

## 문서 저장소

- 메타데이터는 PostgreSQL `documents`, `document_folders`에 저장합니다.
- 원본 파일은 MinIO `documents` 버킷에 저장합니다.
- `allowed_roles` 배열과 Keycloak 토큰의 realm/client roles 교집합으로 다운로드 권한을 판단합니다.
