"""第1回発展: 応答時間と usage metadata を測り JSON に保存する。"""

import argparse
import json
import time
from datetime import datetime, timezone

from google import genai
from google.genai import errors

from app.config import api_error_message, get_api_key

QUESTIONS = [
    "LoRAとは何ですか？ 100字以内で説明してください。",
    "AIE2026の講座の宿題にある3レベルとは何ですか？ 100字以内で答えてください。",
]


def run(models, repeats, pause):
    client = genai.Client(api_key=get_api_key())
    rows = []
    for model in models:
        for question in QUESTIONS:
            for attempt in range(1, repeats + 1):
                start = time.perf_counter()
                try:
                    response = client.models.generate_content(model=model, contents=question)
                    seconds = time.perf_counter() - start
                    usage = response.usage_metadata
                    row = {
                        "model": model, "question": question, "attempt": attempt,
                        "seconds": round(seconds, 3), "status": "ok", "answer": response.text,
                        "input_tokens": usage.prompt_token_count if usage else None,
                        "output_tokens": usage.candidates_token_count if usage else None,
                        "thoughts_tokens": getattr(usage, "thoughts_token_count", None) if usage else None,
                        "total_tokens": usage.total_token_count if usage else None,
                    }
                except errors.APIError as exc:
                    row = {
                        "model": model, "question": question, "attempt": attempt,
                        "seconds": round(time.perf_counter() - start, 3),
                        "status": "error", "error_code": exc.code,
                        "error": api_error_message(exc.code, exc.message),
                    }
                rows.append(row)
                print(f"{model} / 質問{QUESTIONS.index(question) + 1} / {attempt}: "
                      f"{row['status']} {row['seconds']}秒", flush=True)
                if pause:
                    time.sleep(pause)
    return {"created_at_utc": datetime.now(timezone.utc).isoformat(), "results": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--pause", type=float, default=15)
    parser.add_argument("--output", default="lectures/01/benchmark_results.json")
    args = parser.parse_args()
    if args.repeats < 1 or args.pause < 0:
        parser.error("repeats は1以上、pause は0以上にしてください")
    result = run(args.models, args.repeats, args.pause)
    with open(args.output, "w", encoding="utf-8") as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
    print(f"保存: {args.output}")


if __name__ == "__main__":
    main()
