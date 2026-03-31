---
name: llm-review
description: "외부 LLM에게 설계/코드 재검토 요청. Gemini CLI, Codex CLI, Ollama 중 선택 가능. Actions: review, 검토, 재검토, peer review, cross review, llm review. Usage: /llm-review [gemini|codex|ollama] [model] [review instructions]"
---
# LLM Review — 외부 LLM 크로스 리뷰 스킬

현재 대화에서 작성된 설계, 코드, 계획을 외부 LLM(Gemini CLI, Codex CLI, 또는 Ollama)에게 보내 재검토를 받습니다.

## 트리거 조건

- 사용자가 `/llm-review`를 호출할 때
- 설계/코드/계획 작성 후 외부 검토가 필요할 때

## 실행 절차

### 1단계: 인자 파싱

`/llm-review [backend] [model] [추가 지시사항]` 형식으로 파싱합니다.

**backend** (선택, 기본값: gemini):
- `gemini` — Gemini CLI 사용 (`gemini -p`)
- `codex` — Codex CLI 사용 (`codex exec`)
- `ollama` — Ollama 사용 (`ollama run`)

**model** (선택):
- gemini: 생략 시 Gemini CLI 기본 모델 사용, 지정 시 `-m {model}` 플래그 추가
- codex: 생략 시 Codex CLI 기본 모델 사용, 지정 시 `-m {model}` 플래그 추가
- ollama: 생략 시 `qwen3:8b` 사용, 지정 시 해당 모델 사용

**추가 지시사항** (선택):
- backend, model 이후의 나머지 텍스트는 리뷰 지시사항으로 전달
- 예: `/llm-review gemini 보안 취약점 중심으로 검토해줘`
- 예: `/llm-review ollama qwen3:8b 아키텍처 적합성 검토`

**파싱 규칙:**
1. 첫 번째 인자가 `gemini`, `codex`, 또는 `ollama`면 → backend로 사용
2. 첫 번째 인자가 위 셋이 아니면 → backend=gemini, 전체를 추가 지시사항으로 처리
3. backend 다음 인자가 알려진 모델 패턴이면 → model로 사용 (예: `gemini-2.5-pro`, `o3`, `o4-mini`, `qwen3:8b`, `exaone3.5:7.8b`)
4. 모델 패턴: 콜론(`:`)이 포함되거나, `gemini-`, `gpt-`, `claude-`, `o3`, `o4`로 시작하는 문자열
5. 나머지는 모두 추가 지시사항

### 2단계: 리뷰 대상 수집

대화 컨텍스트에서 리뷰할 내용을 수집합니다:

1. **설계 문서가 있는 경우**: 가장 최근 작성/저장된 설계 문서 내용
2. **코드 변경이 있는 경우**: `git diff`로 변경사항 수집
3. **대화 중 계획/분석이 있는 경우**: 해당 내용 요약
4. **위 모두 없는 경우**: 사용자에게 리뷰 대상을 확인

여러 소스가 있으면 모두 포함하되, 토큰 제한을 고려하여 핵심 내용 중심으로 구성합니다.

### 3단계: 리뷰 프롬프트 구성

리뷰 프롬프트를 다음 구조로 구성합니다:

```
당신은 시니어 소프트웨어 아키텍트입니다. 아래 설계/코드를 검토하고 피드백을 주세요.

## 검토 관점
1. 설계의 완성도와 누락된 부분
2. 잠재적 버그나 엣지 케이스
3. 성능/확장성 이슈
4. 보안 취약점
5. 더 나은 대안이 있는지

{추가 지시사항이 있으면 여기에 포함}

## 검토 대상
{수집된 리뷰 내용}

## 응답 형식
- 한국어로 답변
- 문제점은 심각도(높음/중간/낮음)로 분류
- 각 문제에 대한 개선 제안 포함
- 마지막에 전체 평가 요약 (1~2문장)
```

### 4단계: 외부 LLM 호출

**Gemini CLI:**
```bash
gemini -p "{프롬프트}" -m {model} -o text 2>&1
```
- `-p`: 비대화 모드 (headless)
- `-m`: 모델 지정 (생략 시 CLI 기본값)
- `-o text`: 텍스트 출력
- 타임아웃: 300초 (5분)

**Codex CLI:**
```bash
cat "{임시파일}" | codex exec --skip-git-repo-check --ephemeral -m {model} - 2>&1
```
- `-m`: 모델 지정 (생략 시 CLI 기본값, 예: `o3`, `o4-mini`)
- `--skip-git-repo-check`: git repo 외부에서도 실행 가능
- `--ephemeral`: 세션 파일 미저장
- `-`: stdin에서 프롬프트 읽기 (인자 미지정 시)
- 타임아웃: 300초 (5분)

**Ollama:**
```bash
echo "{프롬프트}" | ollama run {model} 2>&1
```
- 기본 모델: `qwen3:8b`
- 타임아웃: 300초 (5분)

**주의사항:**
- 프롬프트에 특수문자가 있으므로 반드시 임시 파일에 저장 후 stdin으로 전달
- 임시 파일은 실행 후 즉시 삭제
- 프롬프트 최대 길이: gemini는 제한 없음, ollama는 모델 컨텍스트에 따라 자동 truncate

### 5단계: 결과 보고

외부 LLM의 응답을 다음 형식으로 출력합니다:

```
## 🔍 외부 LLM 리뷰 결과

- **Backend**: {gemini|ollama}
- **Model**: {사용된 모델명}
- **리뷰 대상**: {설계문서명 또는 변경 요약}

---

{LLM 응답 내용}

---
_Reviewed by {backend} ({model})_
```

## 사용 예시

```
/llm-review                              # Gemini 기본 모델로 리뷰
/llm-review gemini                       # Gemini 기본 모델로 리뷰
/llm-review gemini gemini-2.5-pro        # Gemini 특정 모델로 리뷰
/llm-review codex                        # Codex CLI 기본 모델로 리뷰
/llm-review codex o3                     # Codex CLI o3 모델로 리뷰
/llm-review codex o4-mini               # Codex CLI o4-mini 모델로 리뷰
/llm-review ollama                       # Ollama qwen3:8b로 리뷰
/llm-review ollama exaone3.5:7.8b        # Ollama 특정 모델로 리뷰
/llm-review 보안 관점에서 검토해줘         # Gemini 기본 + 커스텀 지시
/llm-review codex 아키텍처 검토해줘       # Codex + 커스텀 지시
/llm-review ollama qwen3:8b DB 설계 검토  # Ollama 특정 모델 + 커스텀 지시
```

## 에러 처리

| 상황 | 대응 |
|------|------|
| gemini 미설치 | "Gemini CLI가 설치되어 있지 않습니다. `npm install -g @anthropic-ai/gemini-cli` 또는 다른 백엔드를 사용하세요." |
| codex 미설치 | "Codex CLI가 설치되어 있지 않습니다. `npm install -g @openai/codex` 또는 다른 백엔드를 사용하세요." |
| ollama 미실행 | "Ollama가 실행 중이 아닙니다. `ollama serve`로 시작하세요." |
| 모델 미다운로드 (ollama) | "모델 {model}이 없습니다. `ollama pull {model}`로 다운로드하세요." |
| 타임아웃 | "LLM 응답 타임아웃 (300초). 더 작은 모델을 시도하거나 리뷰 내용을 줄여주세요." |
| 리뷰 대상 없음 | 사용자에게 리뷰할 내용을 확인 |
| 빈 응답 | "LLM이 빈 응답을 반환했습니다. 다시 시도하거나 다른 모델을 사용하세요." |

## 주의사항

- 외부 LLM에 전송되는 내용에 시크릿(API 키, 비밀번호 등)이 포함되지 않도록 자동 필터링
- `.env` 파일 내용이나 credential 패턴(`sk-`, `token=` 등)은 `[REDACTED]`로 마스킹
- 프롬프트는 `/tmp/llm_review_*.md`에 임시 저장 후 삭제
- ollama의 `/no_think` 태그는 자동 제거하여 출력
