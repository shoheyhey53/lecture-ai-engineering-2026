# 第3回 解答

## 演習

- 第1回の素の LLM は、講座固有の「宿題の3レベル」について、講座情報を知らずに一般的な推測を挙げた。第3回のエージェント（`gemini-3.5-flash-lite`）は `search_glossary({'query': '3レベル'})` を呼び、用語集を参照して「基礎・実装・発展」と回答した。外部情報を参照することで講座固有の情報を使えたが、参照元自体の正確さや鮮度を保証するものではない。
- 「LoRAとQLoRAの違いは？」では `search_glossary({'query': 'LoRA'})` と `search_glossary({'query': 'QLoRA'})` の2回が呼ばれた。モデルのリクエストは2回（`requests=2`）。
- `make_quiz(lecture: int)` を追加し、指定した回の確認問題を求められたときに使うことを docstring に書いた。実際のモデルは `make_quiz({'lecture': 2})` を呼び、「過学習」の意味を問う問題を出題した。存在しない回には、用語が見つからない旨を返す。

## 宿題

取り組んだレベル：**基礎・実装・発展（a）**。最高レベルは発展。

### 基礎：ツール説明の変更

同じモデル、同じ質問「LoRAとQLoRAの違いは？」で、`search_glossary` の docstring だけを一時的に変更し、`--trace` で各1回比較した。

| ツール説明 | 呼び出し | モデルの requests |
|---|---|---:|
| 用語を1つだけ入れる | `LoRA` と `QLoRA` の2回 | 2 |
| 複数の用語をまとめて入れる | `LoRA QLoRA` の1回 | 2 |

今回、まとめた検索語でも部分一致により両方の項目が見つかり、回答は両者の概要に触れた。ただし検索結果には上限があり、常にまとめて正しく検索できるとは限らない。モデルも毎回同じ呼び方をする保証はない。実用のコードでは元の「1つだけ」の説明に戻した。各回答とトレースは `basic_before.txt`、`basic_after.txt` に保存した。

### 実装：承認付きの学習記録

- `save_learning_log(title, content)` を追加し、`requires_approval=True` で登録した。`DeferredToolRequests` を受け取ると、CLI は呼び出しの内容を表示して `[y/N]` を尋ね、選択を `DeferredToolResults` と会話履歴に渡して続行する。Enter、EOF、`y` / `yes` 以外は拒否する。
- 承認後のみ `learning_log/` に UUID 名の JSON を作る。記録の誤公開を避けるため、そのフォルダは Git の追跡対象から除外した。承認待ちの時点や拒否時にはファイルを作らない。
- TestModel と一時ディレクトリを用いて、承認前と拒否時にファイルがないこと、承認すると1件作成されることを確認した。実際のモデルにも架空のテスト用記録を依頼し、`n` を指定すると、保存をキャンセルした旨を回答した（`approval_denied.txt`）。

### 発展（a）：Google ADK 版との比較

`adk_agent/glossary_agent/` に ADK 版を作り、Pydantic AI 版の `INSTRUCTIONS` と `search_glossary`、`get_lecture_summary`、`make_quiz` を共有した。演習の範囲に合わせて ADK 版には承認付き保存ツールを登録していないため、共有指示に含まれる保存の指示は ADK 版では利用できない。比較した質問は保存を求めない内容である。

同じ `gemini-3.5-flash-lite` に「AIE2026の講座の宿題にある3レベルとは何ですか？」を各1回聞いたところ、どちらも「基礎・実装・発展」と回答した。Pydantic AI 版では `search_glossary({'query': '3レベル'})` の呼び出しを trace で確認できた。ADK の通常 CLI 出力だけではツール呼び出しの詳細は確認していないため、同じ経路で回答したとは断定しない。回答は `pydantic_answer.txt` と `adk_answer.txt` に記録した。どちらも用語集の採点に関する記述を含んだが、実際の評価・提出方法は講座の案内とフォームを確認する。

書き方の違いとして、Pydantic AI 版は `Agent(instructions=...)` を作ってから `tool_plain` でツールを登録し、ADK 版は `Agent` の `instruction` と `tools` にまとめて渡す。ADK は `uv run --with google-adk` で一時的に導入し、依存ファイルは変更していない。各1回答のため、フレームワーク全体の優劣は判断できない。

### 検証・使用ツール

`uv run pytest -q`：14件成功。実験、コード編集、セル・ターミナル操作、記録と集計には Codex を使用した。
