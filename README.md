# CareerChat

채용공고-지원자 역량 갭 분석 및 맞춤 보완 피드백 시스템

## 로컬 개발 환경 개요

CareerChat 로컬 개발 환경은 Frontend, Spring Backend, AI Backend API,
AI Backend Celery worker, 인프라 의존성을 각각 별도 프로세스로 실행한다.

| 구성 요소 | 기본 URL / 포트 | 역할 |
| --- | --- | --- |
| Frontend | `http://localhost:5173` | React/Vite UI |
| Spring Backend | `http://localhost:8080` | 인증, 프로필, 진단, 결과, 챗봇 메시지 저장 |
| AI Backend API | `http://localhost:8000` | 분석 job 생성과 결과 기반 챗봇 응답 API |
| PostgreSQL | `localhost:5432` | Spring 애플리케이션 DB |
| Redis | `localhost:6379` | Celery broker/result backend |
| Qdrant | `http://localhost:6333` | Profile snapshot vector store |

`infra/compose/docker-compose.yml`은 로컬 인프라 의존성 실행용이다.
Spring, AI Backend API, AI worker, Frontend는 로컬 개발 프로세스로 직접 실행한다.

`apps/ai/app/prototype`과 AI sample runner는 reference일 뿐이며 검증 기준으로
사용하지 않는다. 검증은 schema/contract/unit test, frontend lint/build,
필요한 경우 실제 local API/worker 구동 확인 중심으로 진행한다.

## 사전 준비

- Java 21
- Node.js and npm
- Python 3.10+
- Docker Desktop or Docker Engine with Docker Compose
- AI Backend Python 환경 실행용 `uv`

## 1. 환경 파일 준비

예시 파일을 복사해 로컬 env 파일을 만든다.

```bash
cp .env.example .env
cp apps/ai/.env.example apps/ai/.env
cp apps/web/.env.example apps/web/.env
```

로컬 실행 시 확인할 값:

- `GROQ_API_KEY`는 `LLM_PROVIDER=groq`일 때 필요하다.
- `AI_CALLBACK_TOKEN`과 `SPRING_CALLBACK_INTERNAL_TOKEN`은 같은 값이어야 한다.
- `AI_BACKEND_BASE_URL`은 Spring이 호출할 AI Backend API 주소다.
- `AI_CALLBACK_BASE_URL`은 AI Backend callback이 돌아갈 Spring 주소다.

기본 로컬 주소:

```text
AI Backend API: http://localhost:8000
Spring Backend: http://localhost:8080
Frontend API base: /api
Qdrant: http://localhost:6333
Redis broker: redis://localhost:6379/0
Redis result backend: redis://localhost:6379/1
```

루트 `.env`는 Docker Compose 실행에 사용한다. Spring Boot는 `.env`를 자동으로
읽지 않으므로 기본값을 바꾸려면 shell 또는 IDE 실행 설정에 환경변수를 지정한다.
AI Backend와 Vite는 각각 `apps/ai/.env`, `apps/web/.env`를 읽는다.

## 2. 인프라 실행

레포 루트에서 실행한다.

```bash
docker compose --env-file .env -f infra/compose/docker-compose.yml up -d
```

컨테이너 상태 확인:

```bash
docker compose --env-file .env -f infra/compose/docker-compose.yml ps
```

Compose stack 구성:

- `careerchat-postgres`
- `careerchat-redis`
- `careerchat-qdrant`

로컬 인프라 중지:

```bash
docker compose --env-file .env -f infra/compose/docker-compose.yml down
```

로컬 DB, vector store, Redis volume까지 삭제해야 할 때만 `down -v`를 사용한다.

## 3. Spring Backend 실행

Spring은 shell 또는 IDE run configuration의 환경변수를 읽는다.
`apps/backend/src/main/resources/application.properties`의 기본값은 로컬
Compose 기본값과 맞춰져 있다.

새 터미널에서 실행한다.

```bash
cd apps/backend
./gradlew bootRun
```

주요 Spring 환경변수:

| 환경변수 | 로컬 기본값 |
| --- | --- |
| `SPRING_DATASOURCE_URL` | `jdbc:postgresql://localhost:5432/careerchat` |
| `SPRING_DATASOURCE_USERNAME` | `careerchat` |
| `SPRING_DATASOURCE_PASSWORD` | `careerchat` |
| `JWT_SECRET` | `application.properties`의 local development fallback |
| `AI_CALLBACK_TOKEN` | `careerchat-local-ai-callback-token` |
| `AI_BACKEND_BASE_URL` | `http://localhost:8000` |
| `AI_CALLBACK_BASE_URL` | `http://localhost:8080` |
| `AI_REQUEST_TIMEOUT` | `10s` |

Health check:

```bash
curl http://localhost:8080/actuator/health
```

## 4. AI Backend API 실행

새 터미널에서 실행한다.

```bash
cd apps/ai
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

주요 AI Backend 환경변수:

| 환경변수 | 로컬 기본값 |
| --- | --- |
| `LLM_PROVIDER` | `.env.example` 기준 `groq` |
| `GROQ_API_KEY` | Groq 사용 시 필요 |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `LLM_DETERMINISTIC_FALLBACK_ENABLED` | `true` |
| `EMBEDDING_MODEL` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| `QDRANT_URL` | `http://localhost:6333` |
| `QDRANT_COLLECTION_NAME` | `careerchat_profile_chunks` |
| `QDRANT_VECTOR_SIZE` | `384` |
| `REDIS_BROKER_URL` | `redis://localhost:6379/0` |
| `REDIS_RESULT_BACKEND_URL` | `redis://localhost:6379/1` |
| `SPRING_CALLBACK_INTERNAL_TOKEN` | `careerchat-local-ai-callback-token` |
| `CALLBACK_TIMEOUT_SECONDS` | `10` |

`LLM_DETERMINISTIC_FALLBACK_ENABLED`는 분석 pipeline의 fallback/local-dev
동작을 위한 값이다. 결과 기반 챗봇 응답 생성은 configured provider를 사용해야
하며 deterministic fallback에 의존하면 안 된다.

## 5. AI Backend Worker 실행

새 터미널에서 실행한다.

```bash
cd apps/ai
uv run celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

Worker는 Redis의 `analysis.run` task를 처리하고 pipeline 실행 후 Spring callback을
전송한다. Callback 정보는 pipeline step이 아니라 worker/task payload 계층의
책임이다.

## 6. Frontend 실행

새 터미널에서 실행한다.

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:5173`.

Frontend는 기본적으로 `VITE_API_BASE_URL=/api`를 사용한다. Vite dev server는
`apps/web/vite.config.js`에서 `/api` 요청을 `http://localhost:8080`으로 proxy하고
`/api` prefix를 제거한다.

## 7. 로컬 End-to-End 확인

PostgreSQL, Redis, Qdrant, Spring, AI Backend API, AI worker, Frontend가 모두
실행된 상태에서 확인한다.

1. `http://localhost:5173`을 연다.
2. 회원가입 또는 로그인을 진행한다.
3. MyInfo에서 프로필 정보를 입력하고 저장한다.
4. 진단하기 페이지에서 채용공고 1~3개를 제출한다.
5. Spring이 diagnosis를 생성하고 AI Backend analysis job을 요청하는지 확인한다.
6. AI worker가 pipeline을 완료하고 Spring callback을 전송하는지 확인한다.
7. 결과 페이지에서 완료된 진단 결과가 렌더링되는지 확인한다.
8. Result chat panel에서 질문을 전송한다.
9. Spring이 USER 메시지를 저장하고 AI Backend `/chat/responses`를 호출한 뒤
   ASSISTANT 메시지를 저장하며, UI가 두 메시지를 렌더링하는지 확인한다.

## 8. 검증 명령

변경 영역에 맞는 검증을 실행한다.

```bash
cd apps/backend
./gradlew test
```

```bash
cd apps/ai
uv run pytest
```

```bash
cd apps/web
npm run lint
npm run build
```

문서/config 예시만 변경한 경우에도 최소한 변경 파일을 확인하고 다음 명령을 실행한다.

```bash
git diff --check
```
