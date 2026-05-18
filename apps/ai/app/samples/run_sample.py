from __future__ import annotations

import argparse

from app.samples.sample_data import get_sample_payload
from app.services.diagnosis_service import analyze_jobs


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CareerChat AI sample pipeline.")
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=None,
        help="Limit the number of sample job postings to analyze.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of profile chunks to retrieve per requirement.",
    )
    args = parser.parse_args()

    payload = get_sample_payload(max_jobs=args.max_jobs)
    result = analyze_jobs(**payload, top_k=args.top_k)

    print(f"Profile documents: {result['profile_document_count']}")
    print(f"Profile chunks: {result['profile_chunk_count']}")

    print("\n=== Rankings ===")
    for index, ranking in enumerate(result["rankings"], start=1):
        print(
            f"{index}. {ranking['company']} ({ranking['position']}) - {ranking['score']}점"
        )

    if result["match_summary"]:
        print("\n=== Match Summary ===")
        print(result["match_summary"])

    if result["final_report"]:
        print("\n=== Final Report ===")
        print(result["final_report"])


if __name__ == "__main__":
    main()
