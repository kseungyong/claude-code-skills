---
name: stock-screening-report
description: "종목 스크리닝 및 기관투자자용 리서치 리포트를 PDF로 생성. P/E, 매출성장률, 부채비율, 배당수익률, 경제적 해자, 리스크 등급 분석. 사용법: /stock-screening-report 삼성전자,SK하이닉스 [저장경로]"
---

# Stock Screening Report

기관투자자용 종목 스크리닝 리서치 리포트를 **PDF**로 생성하여 저장하는 스킬입니다.

## 인자

$ARGUMENTS 형식:
- `종목1,종목2,종목3` — 기본 저장 경로(~/Downloads/StockReport/)에 PDF 저장
- `종목1,종목2 /path/to/dir` — 지정된 디렉토리에 PDF 저장
- `종목1,종목2 ~/Documents/Reports` — 틸드(~) 경로도 지원

**파싱 규칙:**
1. $ARGUMENTS를 공백으로 분리하여 마지막 토큰이 `/`로 시작하거나 `~`로 시작하면 → 저장 경로로 인식
2. 나머지 토큰을 다시 합쳐서 쉼표(,)로 종목명을 분리
3. 저장 경로가 지정되지 않으면 기본값: `~/Downloads/StockReport/`

**PDF 파일명 규칙:** `SCREENING-REPORT-{YYYYMMDD}-{종목약칭}.pdf`
예: `SCREENING-REPORT-20260404-삼성전자_SK하이닉스.pdf`

만약 종목명이 비어있다면 사용자에게 질문하세요:
"분석할 종목을 쉼표로 구분하여 입력해주세요. (예: 삼성전자,SK하이닉스,네이버)"

## 워크플로우

### Phase 1: 종목 데이터 수집

$ARGUMENTS에서 종목명을 파싱합니다. 각 종목에 대해 **WebSearch 도구**를 사용하여 최신 재무 데이터를 병렬로 수집합니다.

각 종목별 수집 항목:
1. **현재 주가 및 시가총액**
2. **P/E (주가수익비율)** — TTM 기준
3. **매출성장률 (Revenue Growth)** — YoY 기준
4. **부채비율 (Debt-to-Equity Ratio)**
5. **배당수익률 (Dividend Yield)**
6. **업종 및 경쟁사 현황** — 경제적 해자 판단용
7. **최근 실적 및 뉴스** — 리스크 판단용

검색 쿼리 예시:
```
"{종목명} PER 매출성장률 부채비율 배당수익률 2026"
"{종목명} 최근 실적 전망 리스크"
"{종목명} 경쟁우위 시장점유율 해자"
```

**중요**: 데이터를 찾을 수 없는 항목은 "N/A"로 표시하고, 데이터 출처와 기준일을 반드시 명시합니다.

### Phase 2: 스크리닝 분석

수집된 데이터를 기반으로 각 종목을 6개 핵심 지표로 분석합니다.

#### 2-1. Valuation (P/E 분석)

| 등급 | 기준 |
|------|------|
| Undervalued | P/E < 업종 평균의 0.7배 |
| Fair Value | 업종 평균의 0.7~1.3배 |
| Overvalued | P/E > 업종 평균의 1.3배 |
| N/A | 적자 기업 (Negative Earnings) |

#### 2-2. Growth (매출성장률)

| 등급 | 기준 |
|------|------|
| High Growth | YoY > 20% |
| Moderate Growth | YoY 5~20% |
| Low Growth | YoY 0~5% |
| Declining | YoY < 0% |

#### 2-3. Leverage (부채비율)

| 등급 | 기준 |
|------|------|
| Conservative | D/E < 50% |
| Moderate | D/E 50~100% |
| Aggressive | D/E 100~200% |
| High Risk | D/E > 200% |

#### 2-4. Income (배당수익률)

| 등급 | 기준 |
|------|------|
| High Yield | > 4% |
| Moderate Yield | 2~4% |
| Low Yield | 0~2% |
| No Dividend | 0% |

#### 2-5. Economic Moat (경제적 해자)

아래 요소를 종합하여 Wide / Narrow / None 으로 판정:
- **브랜드 파워**: 시장 인지도, 프리미엄 가격 책정 능력
- **네트워크 효과**: 사용자 수 증가에 따른 가치 증대
- **전환비용**: 고객이 경쟁사로 이동하기 어려운 정도
- **원가우위**: 규모의 경제, 독점적 기술/자원
- **무형자산**: 특허, 라이선스, 규제 장벽

#### 2-6. Risk Grade (리스크 등급)

아래 요소를 종합하여 A(Low) / B(Medium) / C(High) / D(Very High) 판정:
- 재무 안정성 (부채비율, 유동비율)
- 실적 변동성 (매출/이익 변동폭)
- 산업 리스크 (규제, 경쟁 강도, 기술 변화)
- 지정학적/매크로 리스크
- 최근 이슈 (소송, 경영권 분쟁, 회계 이슈 등)

### Phase 3: 리포트 출력

아래 형식으로 기관투자자용 리서치 리포트를 출력합니다. **절대 Goldman Sachs 이름이나 브랜드를 포함하지 않습니다.**

---

#### 출력 형식:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
               EQUITY RESEARCH — SCREENING REPORT
                    Institutional Use Only
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: {오늘 날짜}
Analyst: AI Equity Research Division
Coverage: {분석 종목 수}개 종목
Universe: KRX (Korea Exchange)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


I. SCREENING SUMMARY
─────────────────────────────────────────────────────

┌─────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Ticker  │  P/E     │ Rev Grw  │ D/E      │ Div Yld  │  Moat    │  Risk    │
├─────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ {종목1} │ {수치}x  │ {수치}%  │ {수치}%  │ {수치}%  │ {등급}   │ {등급}   │
│ {종목2} │ {수치}x  │ {수치}%  │ {수치}%  │ {수치}%  │ {등급}   │ {등급}   │
│ ...     │          │          │          │          │          │          │
└─────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

Screening Criteria:
  [V] Valuation: {판정}   [G] Growth: {판정}
  [L] Leverage: {판정}    [I] Income: {판정}
  [M] Moat: {판정}        [R] Risk: {판정}


II. INDIVIDUAL STOCK ANALYSIS
─────────────────────────────────────────────────────

(각 종목별로 아래 블록을 반복)

■ {종목명} ({티커/종목코드})
  Sector: {업종}  |  Mkt Cap: {시가총액}  |  Price: {현재가}

  ┌── Valuation ──────────────────────────────────┐
  │ P/E (TTM): {수치}x                            │
  │ Sector Avg P/E: {업종평균}x                    │
  │ Assessment: {Undervalued/Fair/Overvalued}      │
  └───────────────────────────────────────────────┘

  ┌── Growth ─────────────────────────────────────┐
  │ Revenue Growth (YoY): {수치}%                  │
  │ Earnings Growth (YoY): {수치}%                 │
  │ Assessment: {High/Moderate/Low/Declining}      │
  └───────────────────────────────────────────────┘

  ┌── Financial Health ───────────────────────────┐
  │ Debt-to-Equity: {수치}%                        │
  │ Assessment: {Conservative/Moderate/Aggressive} │
  └───────────────────────────────────────────────┘

  ┌── Dividend ───────────────────────────────────┐
  │ Dividend Yield: {수치}%                        │
  │ Payout Ratio: {수치}% (if available)           │
  │ Assessment: {High/Moderate/Low/None}           │
  └───────────────────────────────────────────────┘

  ┌── Economic Moat ──────────────────────────────┐
  │ Moat Rating: {Wide/Narrow/None}                │
  │ Key Sources:                                   │
  │   - {해자 요인 1}                               │
  │   - {해자 요인 2}                               │
  │ Justification: {1~2문장 근거}                   │
  └───────────────────────────────────────────────┘

  ┌── Risk Assessment ────────────────────────────┐
  │ Risk Grade: {A/B/C/D}                          │
  │ Key Risks:                                     │
  │   ⚠ {리스크 1}                                 │
  │   ⚠ {리스크 2}                                 │
  │   ⚠ {리스크 3}                                 │
  └───────────────────────────────────────────────┘

  Investment View: {Positive/Neutral/Negative}
  Conviction Level: {High/Medium/Low}
  One-Line Thesis: {1줄 투자 논리}


III. COMPARATIVE MATRIX
─────────────────────────────────────────────────────

종목 간 비교 매트릭스를 별점(★) 기준으로 시각화:

  Category        {종목1}    {종목2}    {종목3}  ...
  ──────────────────────────────────────────────
  Valuation       ★★★★☆     ★★★☆☆     ★★☆☆☆
  Growth          ★★★☆☆     ★★★★★     ★★★★☆
  Fin. Health     ★★★★★     ★★★☆☆     ★★★★☆
  Dividend        ★★☆☆☆     ★★★★☆     ★★★☆☆
  Moat            ★★★★★     ★★★☆☆     ★★★★☆
  Risk (low=good) ★★★★☆     ★★★☆☆     ★★★★★
  ──────────────────────────────────────────────
  Overall         ★★★★☆     ★★★☆☆     ★★★★☆


IV. SCREENING VERDICT
─────────────────────────────────────────────────────

  ✦ Top Pick: {종합 1위 종목} — {선정 이유 1문장}
  ✦ Runner-up: {2위 종목} — {이유}
  ✦ Watch List: {관심 종목} — {이유}
  ✦ Avoid: {회피 권고 종목} — {이유} (해당 시)


V. KEY RISKS & DISCLAIMERS
─────────────────────────────────────────────────────

  Macro Risks:
  - {시장 전반 리스크 1}
  - {시장 전반 리스크 2}

  Sector-Specific Risks:
  - {섹터별 리스크}

  ※ 본 리포트는 AI 기반 자동 분석 결과이며, 투자 권유가 아닙니다.
  ※ 실제 투자 결정 시 공시자료 및 전문가 의견을 반드시 참고하십시오.
  ※ 데이터 기준일: {기준일} | 출처: 공개 시장 데이터

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    END OF REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 4: PDF 생성 및 저장

리포트 콘솔 출력이 완료되면 **자동으로 PDF를 생성**합니다.

#### Step 1: Markdown 임시 파일 저장

리포트 전체 내용을 `/tmp/stock-report-{YYYYMMDD}.md` 에 Write 도구로 저장합니다.

#### Step 2: 저장 경로 결정

인자 파싱 결과에 따라 저장 경로를 결정합니다:
- 경로 지정됨 → 해당 경로 사용 (디렉토리 없으면 자동 생성)
- 경로 미지정 → `~/Downloads/StockReport/` 사용

#### Step 3: PDF 변환

Bash 도구로 아래 명령을 실행합니다:

```bash
python3 ~/.claude/skills/stock-screening-report/generate_pdf.py \
  /tmp/stock-report-{YYYYMMDD}.md \
  {저장경로}/SCREENING-REPORT-{YYYYMMDD}-{종목약칭}.pdf
```

#### Step 4: 결과 보고

PDF 생성 완료 후 사용자에게 아래 형식으로 보고합니다:

```
PDF 리포트 저장 완료

  파일: {전체 경로}/SCREENING-REPORT-{YYYYMMDD}-{종목약칭}.pdf
  크기: {파일크기}
  종목: {분석 종목 목록}
```

### Phase 5: 추가 옵션

리포트 출력 후 사용자에게 추가 옵션을 제안합니다:

1. **"특정 종목을 더 심층 분석할까요?"** → 해당 종목의 상세 DCF/비교 분석 제공
2. **"종목을 추가/교체하여 다시 분석할까요?"** → Phase 1부터 재실행
3. **"다른 경로에 저장할까요?"** → PDF를 추가 경로에 복사

## 중요 규칙

1. **Goldman Sachs 브랜드 절대 사용 금지** — 리포트 어디에도 Goldman Sachs, GS 등의 이름을 포함하지 않습니다.
2. **데이터 정직성** — 확인할 수 없는 수치는 추정하지 말고 "N/A" 또는 "추정치"로 명시합니다.
3. **출처 명시** — 주요 수치에 대해 데이터 출처(네이버 금융, KRX, 공시 등)를 밝힙니다.
4. **투자 비권유 고지** — 리포트 말미에 반드시 투자 비권유 면책 문구를 포함합니다.
5. **한국어 기반** — 리포트 제목/섹션명은 영문, 분석 내용은 한국어로 작성합니다.
6. **병렬 검색** — 여러 종목의 데이터를 수집할 때 WebSearch를 병렬로 호출하여 속도를 높입니다.
7. **종목명 유연 처리** — "삼전"→"삼성전자", "하닉"→"SK하이닉스" 등 약칭도 인식하여 정식 종목명으로 변환합니다.
8. **PDF 자동 저장** — 리포트는 항상 PDF로 자동 저장됩니다. 콘솔 출력 후 PDF 변환을 건너뛰지 마세요.
9. **저장 경로 기본값** — 경로 미지정 시 `~/Downloads/StockReport/`에 저장합니다.

## 의존성

- **fpdf2** (Python): `pip3 install fpdf2` — PDF 생성 라이브러리
- **한글 폰트**: `/System/Library/Fonts/Supplemental/AppleGothic.ttf` (macOS 기본)
- **PDF 생성 스크립트**: `~/.claude/skills/stock-screening-report/generate_pdf.py`
