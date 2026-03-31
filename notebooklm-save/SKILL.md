---
name: notebooklm-save
description: >
  프로젝트 시작 시 설계 문서(docs/ 또는 현재 대화의 설계 내용)를 NotebookLM에
  자동으로 새 노트북으로 만들고 소스로 저장하는 스킬.

  다음 상황에서 반드시 이 스킬을 사용하세요:
  - 사용자가 "notebooklm에 저장해줘", "notebooklm 노트 만들어줘"라고 할 때
  - /plan-to-doc 실행 후 "notebooklm에도 올려줘"라고 할 때
  - 새 프로젝트 시작 시 "notebooklm 연동해줘"라고 할 때
---

# NotebookLM Save Skill

프로젝트 설계 문서를 Google NotebookLM에 새 노트북으로 자동 생성하고 소스로 저장합니다.

---

## 실행 절차

### Step 1. 저장할 문서 확인

아래 순서로 소스 문서를 탐색합니다:

1. `docs/` 폴더에 오늘 날짜 설계 문서 존재 여부 확인
2. 없으면 `docs/` 내 가장 최근 `.md` 파일 사용
3. 없으면 현재 대화에서 생성된 설계 내용을 임시 파일로 저장

```bash
# docs/ 폴더 최근 파일 확인
ls -t docs/*.md 2>/dev/null | head -1
```

임시 파일 경로: `/tmp/notebooklm-{프로젝트명}-{YYYYMMDD}.md`

---

### Step 2. 프로젝트명 추출

```bash
basename $(pwd)
```

---

### Step 3. Chrome에서 NotebookLM 열기

`mcp__claude-in-chrome__tabs_context_mcp`로 현재 탭 확인 후,
NotebookLM이 열려있지 않으면 새 탭 생성:

```
URL: https://notebooklm.google.com
```

페이지 로딩 완료까지 대기 (로그인 여부 확인).

**로그인 안 된 경우**: 사용자에게 로그인 요청 후 계속 진행.

---

### Step 4. 새 노트북 생성

NotebookLM 홈에서:

1. "새 노트북" 버튼 클릭 (`mcp__claude-in-chrome__find` 또는 `mcp__claude-in-chrome__computer`)
2. 노트북 제목 입력: `{프로젝트명} - {YYYY-MM-DD}`
   - 예: `kdsys-homepage - 2026-03-10`

---

### Step 5. 소스 업로드

새 노트북이 열리면:

1. "소스 추가" 또는 "+" 버튼 클릭
2. "파일 업로드" 선택
3. Step 1에서 확인한 `.md` 파일 업로드 (`mcp__claude-in-chrome__upload_image` 또는 파일 선택 UI)
4. 업로드 완료 대기

**지원 형식**: `.md`, `.pdf`, `.txt`
- `.md` 파일이 업로드 안 될 경우 → `.txt`로 복사 후 재시도:

```bash
cp docs/{파일명}.md /tmp/{파일명}.txt
```

---

### Step 6. 노트북 URL 저장 (선택)

업로드 완료 후 현재 URL을 복사해 사용자에게 전달합니다.

URL 형식 예시: `https://notebooklm.google.com/notebook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

## 완료 후 출력 메시지

```
✅ NotebookLM 노트북이 생성되었습니다.
📓 노트북명: {프로젝트명} - {YYYY-MM-DD}
📄 소스: {파일명}
🔗 URL: {노트북 URL}
```

---

## 오류 처리

| 상황 | 대응 |
|------|------|
| NotebookLM 로그인 안 됨 | 사용자에게 로그인 요청 후 재시도 |
| docs/ 문서 없음 | 현재 대화 내용으로 임시 `.md` 생성 |
| `.md` 업로드 불가 | `.txt`로 변환 후 재시도 |
| 노트북 생성 UI 변경 | `mcp__claude-in-chrome__get_page_text`로 현재 페이지 구조 파악 후 재시도 |
| 브라우저 자동화 2회 이상 실패 | 사용자에게 수동 안내 (노트북 URL + 파일 경로 제공) |

---

## plan-to-doc와 연계 사용

`/plan-to-doc` 실행 후 바로 이어서 호출하면 설계 문서를 자동으로 NotebookLM에 저장합니다:

```
/plan-to-doc → /notebooklm-save
```

또는 한 번에:

```
계획 작성 후 notebooklm에도 저장해줘
```

---

## 주의사항

- NotebookLM은 **공개 API가 없으므로** 브라우저 자동화 기반으로 동작합니다.
- Chrome이 실행 중이어야 하며, Google 계정으로 로그인되어 있어야 합니다.
- NotebookLM UI 변경 시 동작이 불안정해질 수 있습니다.
- 동일 프로젝트명으로 여러 번 실행하면 날짜가 다르므로 별도 노트북이 생성됩니다.
