"""第1回: Gemini への単発質問と、会話履歴を保った対話。

使い方: uv run python -m app.ask "LoRAとは何ですか？"
        uv run python -m app.ask --chat
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def print_usage(response) -> None:
    usage = response.usage_metadata
    if usage is not None:
        print(f"[トークン] 入力: {usage.prompt_token_count} / 出力: {usage.candidates_token_count}")


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)
    print_usage(response)
    return response.text


def chat_loop(client, input_fn=input) -> None:
    """同一セッションに履歴を保持し、終了まで対話する。"""
    chat = client.chats.create(model=MODEL)
    print("対話を開始します。終了するには /quit と入力してください。")
    while True:
        try:
            question = input_fn("あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n対話を終了します。")
            break
        if question.lower() in {"/quit", "/exit"}:
            print("対話を終了します。")
            break
        if not question:
            continue
        try:
            response = chat.send_message(question)
        except errors.APIError as exc:
            print(api_error_message(exc.code, exc.message))
            continue
        print_usage(response)
        print(f"AI: {response.text}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=None)
    parser.add_argument("--chat", action="store_true", help="会話履歴を保って対話する")
    args = parser.parse_args()
    if args.chat and args.question is not None:
        parser.error("--chat と質問引数は同時に指定できません")
    print(f"[model] {MODEL}")
    try:
        if args.chat:
            chat_loop(genai.Client(api_key=get_api_key()))
        else:
            question = args.question or DEFAULT_QUESTION
            print(f"[質問] {question}\n")
            print(ask(question))
    except errors.APIError as exc:
        print(api_error_message(exc.code, exc.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
