# 포켓몬GO 도감 + 레이드/PvP 기능 설정 가이드

이 가이드는 포켓몬GO Tracker 프로젝트에 추가된 **한글 중심 포켓몬 도감, 레이드 카운터, PvP 파티 순위** 기능에 대한 전체 설명과 사용 방법을 다룹니다.

---

## 📋 목차

1. [기능 개요](#기능-개요)
2. [백엔드 구조](#백엔드-구조)
3. [데이터 파일 관리](#데이터-파일-관리)
4. [API 엔드포인트](#api-엔드포인트)
5. [프론트엔드 구현 가이드](#프론트엔드-구현-가이드)
6. [시즌 데이터 업데이트 방법](#시즌-데이터-업데이트-방법)

---

## 🎯 기능 개요

### 구현된 기능들:

#### 1. **포켓몬 도감 (Pokédex)**
- 전체 포켓몬 리스트 & 검색 (한글/영문)
- 상세 정보: 기본 스탯, 타입, 진화 라인
- 기술 정보: 평타/차징 기술 (한글 이름)
- 레거시 기술 표시
- 레이드 100% IV CP 계산 (레벨 20/25)
- 현재 시즌 티어 정보

#### 2. **레이드 카운터 (Raid Counters)**
- 레이드 보스별 추천 팀 구성
- 각 팀원의 추천 기술 조합
- 역할 설명 (딜러, 탱커 등) - 한글

#### 3. **최강 레이드 공격자 (Top Raid Attackers)**
- 현재 시즌 S~A 티어 레이드 공격자
- 타입별 필터링 가능
- 추천 기술 세트

#### 4. **PvP 파티 순위 (PvP Party Rankings)**
- 슈퍼/하이퍼/마스터리그별 파티 순위 1~20위
- 3마리 팀 구성 + 추천 기술
- 예상 레이팅 & 전략 설명 (한글)

---

## 🏗️ 백엔드 구조

### 디렉토리 구조:

```
backend/
├── app/
│   ├── api/
│   │   ├── pokedex.py      # 도감 API
│   │   ├── raids.py         # 레이드 API
│   │   ├── pvp.py           # PvP API
│   │   └── admin.py         # 데이터 리로드 API
│   ├── models/
│   │   └── pokedex.py       # SQLAlchemy 모델
│   ├── schemas/
│   │   └── pokedex.py       # Pydantic 스키마
│   ├── services/
│   │   └── pokedex_data_loader.py  # JSON 데이터 로더
│   ├── utils/
│   │   └── cp_calculator.py  # CP 계산 함수
│   └── main.py              # FastAPI 앱
├── data/                    # JSON 데이터 파일
│   ├── pokemon_base.json
│   ├── moves.json
│   ├── pokemon_moves.json
│   ├── seasonal_tiers.json
│   ├── raid_counters.json
│   └── pvp_party_rankings.json
```

### 주요 컴포넌트:

1. **Data Loader** (`pokedex_data_loader.py`)
   - JSON 파일을 로드하고 캐싱
   - 포켓몬, 기술, 티어 정보 조회 메서드 제공
   - 현재 시즌 자동 감지

2. **CP Calculator** (`cp_calculator.py`)
   - 포켓몬GO CP 계산 공식 구현
   - 레이드 100% IV CP 계산 (레벨 20/25)

3. **API Endpoints**
   - `/api/pokedex` - 도감 리스트 & 상세
   - `/api/raids` - 레이드 카운터 & 최강 공격자
   - `/api/pvp/party-rankings` - PvP 파티 순위
   - `/api/admin` - 데이터 리로드 & 통계

---

## 📁 데이터 파일 관리

### 1. `pokemon_base.json` - 포켓몬 기본 정보

```json
[
  {
    "pokedex_number": 384,
    "name_en": "Rayquaza",
    "name_ko": "레쿠쟈",
    "types": ["Dragon", "Flying"],
    "base_attack": 284,
    "base_defense": 170,
    "base_stamina": 213,
    "image_url": "https://...",
    "evolutions": []
  }
]
```

### 2. `moves.json` - 기술 정보

```json
[
  {
    "id": 1,
    "move_id": "dragon_tail",
    "name_en": "Dragon Tail",
    "name_ko": "드래곤테일",
    "type": "Dragon",
    "power": 15,
    "energy": 9,
    "move_type": "fast",
    "is_legacy": false
  }
]
```

### 3. `pokemon_moves.json` - 포켓몬-기술 매핑

```json
[
  {
    "pokemon_id": 384,
    "move_id": "dragon_tail",
    "category": "fast"
  }
]
```

### 4. `seasonal_tiers.json` - 시즌별 티어 정보

```json
[
  {
    "season_id": "2025_season1",
    "season_name_ko": "2025 시즌1",
    "start_date": "2025-01-01",
    "end_date": "2025-03-31",
    "pokemon_id": 384,
    "raid_tier": "5",
    "raid_attack_tier": "S",
    "gbl_great_tier": "NONE",
    "gbl_ultra_tier": "A",
    "gbl_master_tier": "S",
    "raid_role_ko": "드래곤 딜러"
  }
]
```

### 5. `raid_counters.json` - 레이드 카운터 팀

```json
[
  {
    "boss_pokemon_id": 384,
    "season_id": "2025_season1",
    "recommended_teams": [
      {
        "name_ko": "얼음 타입 카운터 팀",
        "description_ko": "레쿠쟈의 드래곤/비행 타입에 강한 얼음 타입 중심 파티",
        "members": [
          {
            "pokemon_id": 445,
            "pokemon_name_ko": "한카리아스",
            "fast_move_id": "mud_shot",
            "charged_move_id": "outrage",
            "role_ko": "드래곤 딜러"
          }
        ]
      }
    ]
  }
]
```

### 6. `pvp_party_rankings.json` - PvP 파티 순위

```json
[
  {
    "league": "Great",
    "season_id": "2025_season1",
    "rankings": [
      {
        "rank": 1,
        "team": [
          {
            "pokemon_id": 448,
            "pokemon_name_ko": "루카리오",
            "fast_move_id": "counter",
            "charged_move_id": "aura_sphere"
          }
        ],
        "estimated_rating": 2650,
        "notes_ko": "메타 커버 우수, ABB 밸런스 완벽"
      }
    ]
  }
]
```

---

## 🌐 API 엔드포인트

### 1. 포켓몬 도감 API

#### `GET /api/pokedex`
포켓몬 리스트 또는 검색

**Query Parameters:**
- `search` (optional): 한글 또는 영문 이름으로 검색
- `skip` (default: 0): 페이지네이션 오프셋
- `limit` (default: 100): 최대 결과 수

**Response:**
```json
[
  {
    "id": 384,
    "pokedex_number": 384,
    "name_en": "Rayquaza",
    "name_ko": "레쿠쟈",
    "types": ["Dragon", "Flying"],
    "image_url": "https://..."
  }
]
```

#### `GET /api/pokedex/{pokemon_id}`
포켓몬 상세 정보

**Response:**
```json
{
  "id": 384,
  "name_ko": "레쿠쟈",
  "name_en": "Rayquaza",
  "types": ["Dragon", "Flying"],
  "base_attack": 284,
  "base_defense": 170,
  "base_stamina": 213,
  "moves_fast": [...],
  "moves_charged": [...],
  "raid_perfect_cp": {
    "lv20_cp_100": 2102,
    "lv25_cp_100": 2631
  },
  "current_season": {
    "season_id": "2025_season1",
    "raid_tier": "5",
    "gbl_master_tier": "S",
    ...
  }
}
```

### 2. 레이드 API

#### `GET /api/raids/{boss_id}/counters`
레이드 보스 카운터 팀

**Response:**
```json
{
  "boss_id": 384,
  "boss_name_ko": "레쿠쟈",
  "boss_types": ["Dragon", "Flying"],
  "recommended_teams": [...]
}
```

#### `GET /api/raids/top-attackers`
최강 레이드 공격자

**Query Parameters:**
- `type` (optional): 타입 필터 (예: "Dragon", "Fire")
- `min_tier` (default: "A"): 최소 티어 (S 또는 A)

### 3. PvP API

#### `GET /api/pvp/party-rankings`
PvP 파티 순위

**Query Parameters:**
- `league` (default: "Great"): "Great", "Ultra", or "Master"
- `limit` (default: 20): 반환할 순위 수

**Response:**
```json
{
  "league": "Great",
  "league_name_ko": "슈퍼리그",
  "season_id": "2025_season1",
  "rankings": [
    {
      "rank": 1,
      "team": [...],
      "estimated_rating": 2650,
      "notes_ko": "메타 커버 우수, ABB 밸런스 완벽"
    }
  ]
}
```

### 4. Admin API

#### `POST /api/admin/reload-data`
데이터 파일 리로드 (서버 재시작 없이)

#### `GET /api/admin/data-stats`
로드된 데이터 통계

---

## 🎨 프론트엔드 구현 가이드

프론트엔드는 Next.js 기반으로 구현해야 합니다. 아래는 각 페이지별 구현 가이드입니다.

### 필요한 페이지들:

1. **`/pokedex`** - 포켓몬 리스트 & 검색
2. **`/pokedex/[id]`** - 포켓몬 상세 정보
3. **`/raids/[bossId]`** - 레이드 보스 카운터
4. **`/raids/top`** - 최강 레이드 공격자
5. **`/pvp/party-rankings`** - PvP 파티 순위

### 주요 UI 요소:

#### 포켓몬 카드 컴포넌트
```tsx
- 포켓몬 이미지
- 한글 이름 (크게)
- 영문 이름 (작게)
- 타입 배지
- 클릭 시 상세 페이지로 이동
```

#### 기술 표시
```tsx
- 기술 이름 (한글 우선)
- 타입 아이콘
- 위력/에너지
- 레거시 배지 (is_legacy=true일 때)
```

#### PvP 팀 카드
```tsx
- 순위 표시
- 3마리 포켓몬 이미지 + 이름
- 각 포켓몬의 기술
- 예상 레이팅
- 전략 설명 (notes_ko)
```

---

## 🔄 시즌 데이터 업데이트 방법

### 새 시즌 추가 시:

1. **`seasonal_tiers.json` 업데이트**
   ```json
   {
     "season_id": "2025_season2",
     "season_name_ko": "2025 시즌2",
     "start_date": "2025-04-01",
     "end_date": "2025-06-30",
     ...
   }
   ```

2. **`raid_counters.json` 업데이트**
   - 새 레이드 보스 추가
   - season_id 업데이트

3. **`pvp_party_rankings.json` 업데이트**
   - 새 메타에 맞춰 순위 조정

4. **서버에 반영**
   ```bash
   # 방법 1: 서버 재시작
   cd backend
   source venv/bin/activate
   python run.py

   # 방법 2: API로 리로드 (서버 재시작 없이)
   curl -X POST http://localhost:8000/api/admin/reload-data
   ```

### 새 포켓몬 추가:

1. **`pokemon_base.json`에 추가**
2. **`moves.json`에 신규 기술 추가** (필요시)
3. **`pokemon_moves.json`에 기술 매핑 추가**
4. **데이터 리로드**

---

## 🧪 테스트 방법

### 1. 백엔드 API 테스트

```bash
# 서버 시작
cd backend
source venv/bin/activate
python run.py

# API 테스트
curl http://localhost:8000/api/pokedex
curl http://localhost:8000/api/pokedex/384
curl http://localhost:8000/api/raids/384/counters
curl http://localhost:8000/api/pvp/party-rankings?league=Great
```

### 2. Swagger UI로 테스트
브라우저에서 `http://localhost:8000/docs` 접속하여 인터랙티브 API 테스트

---

## 📚 추가 리소스

- FastAPI 공식 문서: https://fastapi.tiangolo.com
- Next.js 공식 문서: https://nextjs.org/docs
- PokeAPI (참고용): https://pokeapi.co
- PvPoke (PvP 데이터 참고): https://pvpoke.com

---

## 🐛 문제 해결

### 데이터가 로드되지 않을 때:
```bash
# 데이터 파일 위치 확인
ls backend/data/

# 데이터 통계 확인
curl http://localhost:8000/api/admin/data-stats
```

### CORS 에러:
`backend/app/core/config.py`의 `ALLOWED_ORIGINS`에 프론트엔드 URL 추가

### JSON 파일 수정 후 반영 안 될 때:
```bash
curl -X POST http://localhost:8000/api/admin/reload-data
```

---

## ✅ 완료된 백엔드 기능

- ✅ SQLAlchemy 모델
- ✅ Pydantic 스키마
- ✅ JSON 데이터 로더
- ✅ CP 계산 함수
- ✅ 도감 API
- ✅ 레이드 API
- ✅ PvP API
- ✅ Admin API
- ✅ 예제 데이터 (10개 포켓몬)
- ✅ FastAPI main.py 라우터 등록

## 🎯 다음 단계: 프론트엔드 구현

백엔드가 완성되었으므로, 이제 Next.js 프론트엔드를 구현하면 됩니다!
