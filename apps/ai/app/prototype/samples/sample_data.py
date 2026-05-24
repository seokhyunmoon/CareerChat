from __future__ import annotations

from copy import deepcopy
from typing import Any


SAMPLE_USER = {
    "user_id": 1,
    "email": "moon@example.com",
    "password_hash": "hashed_password_example",
    "name": "문석현",
    "telephone": "01012345678",
    "created_at": "2026-04-16 10:00:00",
    "updated_at": "2026-04-16 10:00:00",
}

SAMPLE_PROFILE = {
    "profile_id": 1,
    "user_id": 1,
    "experience_level": "ENTRY",
    "created_at": "2026-04-16 10:05:00",
    "updated_at": "2026-04-16 10:05:00",
}

SAMPLE_EDUCATION = [
    {
        "edu_id": 1,
        "profile_id": 1,
        "school_name": "연세대학교",
        "grad_status": "졸업 예정",
        "degree": "학사",
        "major": "응용정보공학",
        "start_date": "2019-09-01",
        "end_date": None,
    }
]

SAMPLE_WORK_EXPERIENCE = [
    {
        "career_id": 1,
        "profile_id": 1,
        "company_name": "A*STAR Institute of High Performance Computing (IHPC)",
        "employment_type": "Research Internship",
        "position": "Research Intern",
        "start_date": "2025-09-01",
        "end_date": "2025-12-19",
        "description": """
Python 기반으로 금융 문서 질의응답용 RAG 시스템 Financial Document Analyzer를 개발했다.
초기에는 단순 dense vector search 기반 baseline retrieval pipeline을 구현하고,
FinanceBench 벤치마크를 기준으로 정답 수와 retrieval 품질을 측정했다.
성능 개선을 위해 Unstructured 기반 문서 파싱 결과를 활용하여
PDF의 title, header, footer, table 등 구조 요소를 반영한 element-based chunking 로직을 설계했다.
특히 section title을 독립 chunk로 두지 않고 metadata로 분리해 본문과 함께 유지하도록 구성하여
검색 시 low-context title chunk가 과도하게 반환되는 문제를 줄였다.
retrieval 단계에서는 semantic vector search와 BM25 keyword search를 결합한 hybrid retrieval 구조를 구현했고,
두 검색 결과를 통합하기 위해 Reciprocal Rank Fusion(RRF)을 적용했다.
이후 상위 후보 chunk를 대상으로 LLM 기반 reranking 단계를 추가하여 relevance를 재평가하고,
최종 answer generation에 더 정밀한 context가 전달되도록 개선했다.
또한 각 chunk에 대해 LLM 기반 summary/keyword metadata를 생성하는 파이프라인을 구성했고,
metadata generation 속도 병목을 해결하기 위해 Python thread pool 기반 병렬 처리를 적용했다.
실험 과정에서는 batch evaluation 스크립트를 반복 실행하며 retrieval 성능을 수치화했고,
오답 케이스와 irrelevant chunk를 직접 분석해 chunking, retrieval, reranking 전략을 단계적으로 개선했다.
이 과정에서 advanced chunking, hybrid retrieval, RRF, reranking, benchmark-driven evaluation 중심의 RAG 시스템 최적화 경험을 쌓았다.
        """.strip(),
    }
]

SAMPLE_PROJECTS = [
    {
        "project_id": 1,
        "profile_id": 1,
        "project_name": "CareerChat",
        "description": """
Spring Boot와 FastAPI 기반으로 개발자 채용공고 비교 분석 서비스 CareerChat의 시스템 구조를 설계하고 프로토타입을 구현했다.
백엔드 영역은 Spring Boot를 중심으로 사용자 인증, 프로필 관리, 진단 요청, 결과 조회 API 구조를 설계했고,
AI 분석 영역은 FastAPI + LangGraph 기반으로 공고 요구사항 추출, 공고-프로필 비교 분석, 리포트 생성, 챗봇 응답 흐름을 분리했다.
데이터 저장 구조는 PostgreSQL 기준으로 Users, Profiles, Education, WorkExperience, Projects, Diagnoses, JDResults, ChatMessages 테이블을 설계했다.
비교 진단은 사용자가 입력한 채용공고 2~3개와 저장된 프로필 정보를 기반으로 동작하도록 구성했고,
공고별 적합도 점수, 강점 요약, 부족 역량, 강조 포인트를 생성하는 구조를 정의했다.
검색 및 분석 단계에서는 HuggingFace sentence-transformers 임베딩과 FAISS/Qdrant 기반 vector retrieval 구조를 고려했고,
Groq API 기반 LLM을 사용해 공고 요구사항 추출과 최종 리포트 생성을 수행하는 흐름을 설계했다.
또한 Redis와 Celery를 활용한 비동기 진단 처리 구조를 적용해
진단 요청 생성과 실제 AI 분석 작업을 분리하는 아키텍처를 구성했다.
프론트엔드에서는 Next.js 기반으로 로그인, 내 정보 입력, 진단하기, 결과 리포트 및 챗봇 UI 흐름을 설계했고,
전체 서비스는 Docker Compose 기반으로 로컬/EC2 배포가 가능하도록 구조화했다.
이 프로젝트를 통해 백엔드 API 설계, AI 서비스 오케스트레이션, 데이터 모델링, 비동기 처리, RAG 기반 서비스 설계 경험을 쌓았다.
        """.strip(),
    }
]

SAMPLE_ACHIEVEMENTS = [
    {
        "award_id": 1,
        "profile_id": 1,
        "title": "OPIc IH",
        "issuer": "ACTFL",
        "score_or_grade": "IH",
        "acquired_date": "2025-03-17",
    }
]

SAMPLE_JOB_POSTINGS = [
    {
        "company_name": "토스",
        "position": "AI Engineer",
        "content": """
합류하게 될 팀에 대해 알려드려요

AI Platform 팀은 "AI 기술을 누구나 빠르고 안정적으로 사용할 수 있는 플랫폼으로 만든다"는 미션을 가지고, 토스 전반의 AI 활용을 기술적으로 지원하고 있어요.
Retrieval-Augmented Generation, Agent, Assistant 등 새로운 방식의 AI 시스템이 빠르게 실험되고 안정적으로 운영될 수 있도록, 필요한 도구와 플랫폼을 만들고 있어요.
우리가 만드는 플랫폼은 단순한 툴셋이 아니라, AI 기술이 더 많은 팀에서 실제로 쓰일 수 있게 확장성을 갖춘 구조로 설계돼요.
아직 정답이 정해지지 않은 문제들을 다루는 만큼, 기술적인 방향을 함께 고민하고 구조화해나가는 역할이 중요해요.

합류하면 함께 할 업무에요

Retrieval, Generation, Vector Search 등 LLM 기반 컴포넌트를 묶어 다양한 팀이 재사용할 수 있도록 플랫폼화해요.
SaaS & Self-hosted LLM 모두 연동하는 기능을 제공하고 안정적인 운영을 제공해요.
Prompt, Tool, 컨텍스트 구성 등 Agent 시스템을 더 쉽게 만들고 실험할 수 있도록 기반을 설계해요.
실험 이후 서비스에서도 안정적으로 작동할 수 있도록, RAG, Agent 들의 서빙과 운영 흐름을 정리하고 도구화해요.
Agent 의 성능과 품질을 정량적으로 평가할 수 있는 기반을 만들고 플랫폼으로 제공해요.
팀 내부뿐 아니라 다른 팀에서도 AI 시스템을 빠르게 실험하고 적용할 수 있도록 공통화된 환경과 경험을 설계해요.
정형화되지 않은 기술 요소들을 구조화하고, 점점 더 넓은 문제로 확장될 수 있도록 방향을 만들어가요.

이런 분과 함께하고 싶어요

LLM, RAG, Agent와 같은 기술을 실제 문제에 적용해본 경험이 있다면 함께하고 싶어요
구조화되지 않은 문제를 기술적으로 정의하고, 시스템적으로 해결해본 분이면 좋아요
여러 팀과 협업하며 기술을 제품처럼 만들고 운영해본 분과 함께하고 싶어요
새로운 기술 흐름을 빠르게 따라가고, 그 흐름을 팀 내에 자연스럽게 녹여낸 경험이 있다면 좋아요
복잡한 AI 시스템을 단순하고 일관된 사용자 경험으로 풀어내는 데 관심이 있다면 함께하고 싶어요

이런 분이면 더 좋아요

Retrieval, Generation, Vector Search 등 RAG 구성 요소를 단독으로 설계하고, 시스템 수준에서 통합해본 경험이 있다면 좋아요
다양한 LLM 서빙 구조(OpenAI API, HuggingFace, vLLM 등)를 실제 서비스 상황에 맞춰 선택하고 운영해본 분이면 함께하고 싶어요
다양한 목적을 가진 Agent 들을 구조화하고 서비스에 적용하여 운영해본 경험이 있다면 더욱 환영이에요.
플랫폼 사용자(내부 개발자, 모델 엔지니어 등)의 요구사항을 바탕으로 실험 환경이나 도구를 주도적으로 설계해본 경험이 있다면 좋아요
공통 플랫폼이나 RAG 기반 시스템을 다수의 프로젝트나 도메인에 확장 가능한 형태로 만들고 운영한 경험이 있다면 특히 함께하고 싶어요
        """.strip(),
    },
    {
        "company_name": "네이버",
        "position": "3DVision Researcher",
        "content": """
What You'll Do

· 실내외 다양한 환경에서 강건하게 동작하는 단안카메라를 이용한 3D Vision 기술 연구
· 디지털 트윈 기술을 모바일, AR 글래스 등 다양한 디바이스 및 응용 서비스로 확장하기 위한 플랫폼 기술 개발 및 최적화

Required Skills

· 경력구분 : 경력
· 해당 분야 석사 학위 후 3년 이상의 연구/개발 경력 또는 박사학위 소지자
  ※ 박사학위 소지자의 경우 회사 경력이 없더라도 지원 가능함
· 3D Vision(Geometry) 및 Computer Vision에 대한 전반적인 이해
· 아래 분야 (1개 이상)에 대한 경험자를 모십니다.
 - 3D Vision (e.g., MASt3R, VGGT, Multi-view Geometry)
 - 딥러닝 기술을 접목한 Visual SLAM / Visual Odometry / SfM / Visual Localization
 - Pose graph optimization / Bundle adjustment / Non-linear optimization

Preferred Skills

· Large-scale 데이터 학습 및 활용 경험
· k8s 기반 클러스터 환경에서 네트워크 학습 또는 개발 경력
· 관련한 다양한 프로젝트를 주도적으로 수행한 경험
· 해당 분야에서의 국제 학술활동 경험 (CVPR, ICCV, ECCV, Siggraph, NeurIPS, ICRA, IROS 등)

채용하고 싶은 사람

· Self-Motivated Team Player
· 스스로 성장의 방향을 정하고, 완성도를 위해 창의적으로 시도하며 끝까지 고민하고 실행하는 사람
· 각자의 전문성을 존중하는 수평적 협업 속에서, 열린 소통으로 문제를 함께 해결하는 사람
        """.strip(),
    },
]


def get_sample_payload(max_jobs: int | None = None) -> dict[str, Any]:
    job_postings = deepcopy(SAMPLE_JOB_POSTINGS)

    if max_jobs is not None:
        job_postings = job_postings[:max_jobs]

    return {
        "user": deepcopy(SAMPLE_USER),
        "profile": deepcopy(SAMPLE_PROFILE),
        "education": deepcopy(SAMPLE_EDUCATION),
        "work_experience": deepcopy(SAMPLE_WORK_EXPERIENCE),
        "projects": deepcopy(SAMPLE_PROJECTS),
        "achievements": deepcopy(SAMPLE_ACHIEVEMENTS),
        "job_postings": job_postings,
    }
