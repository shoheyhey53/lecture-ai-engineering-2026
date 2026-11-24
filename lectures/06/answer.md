# 第6回 演習・宿題

## 演習

実行日：2026年11月24日。回答モデルは `gemini-3.5-flash-lite`。第6回開始タグから別の作業ディレクトリを作り、Gemini APIを使って実行した。実行ログは[logs/](logs/)に保存した。

- **STEP 1**：直接登録されたツールは `search_materials`、MCP用語集から公開されたツールは `glossary_search_glossary`。どちらもモデルには名前・説明・引数を持つツールとして見える。[直接登録](logs/step1_direct.txt)／[MCP](logs/step1_mcp.txt)
- **STEP 2**：[tool call] `glossary_search_glossary({'query': '3レベル'})`。用語集の定義が返り、モデル応答は2回だった。[ログ](logs/step2_glossary.txt)
- **STEP 3**：設定にfetchを追加。ツールが2個になり、[tool call] `fetch_fetch({'url': 'https://modelcontextprotocol.io/'})` で取得して回答した。実際にはトップページが導入ページへリダイレクトされた。[ログ](logs/step3_fetch.txt)
- **STEP 4**：設定にAWS KnowledgeのURLを追加。ツールが7個になり、`aws_aws___search_documentation` が2回呼ばれた。検索語は `Amazon S3 バージョニング 概要` と `Using versioning S3 developer guide`、いずれも `topics=['general']`。応答は3回で、S3のバージョニングを説明した。[ログ](logs/step4_aws.txt)

MCPはモデルが道具を受け取る共通の仕組みで、ローカルで動かす用語集／fetchと、URLで接続するAWSのサーバーを設定で切り替えられる。外部サーバーに渡した検索語は提供元に送られる。また、サーバー提供者が記述した説明文もモデルに渡る。用語集の回答には「原則として採点しない」という記載もあったが、提出条件や採点の扱いは講座の最新の案内を確認する必要がある。

提供元・取り扱いの確認：fetchは[MCPの公開リポジトリ](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)のサーバーで、提供元は内部IPへのアクセスに関するリスクを注意している。演習の指定バージョン `2026.11.11` を使い、private IPやrobots.txtの制限を外すオプションは付けていない。AWS Knowledgeは[AWSの公開サーバー](https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server)で、今回は公開資料に関する質問のみを送った。

## 宿題

基礎・実装・発展に取り組んだ。

### 基礎：要点ツールの公開

サーバー側の `app/mcp_server.py` に `server.tool()(tools.get_lecture_summary)` を追加した。演習後のクライアントコードと接続先設定を変更せずに一覧を確認し、`glossary_get_lecture_summary` が増えた。「第2回では何を学びますか？」に対して、実際に次の呼び出しが行われた。

```text
[tool call]   glossary_get_lecture_summary({'lecture': 2})
```

MCPサーバーから第2回の要点が戻り、モデルはLoRAやファインチューニングなどを説明した。[一覧](logs/basic_list.txt)／[回答とtrace](logs/basic_summary.txt)

### 実装：確認クイズツール

`app/mcp_server.py` に `make_quiz(lecture: int)` を実装して公開した。第1〜3回のクイズを返し、それ以外は利用できる回を案内する。

「第99回のクイズを作って」への実行結果：

```text
[tool call]   glossary_make_quiz({'lecture': 99})
[tool return] glossary_make_quiz -> 第99回のクイズはありません。利用できるのは第1〜3回です。…
```

モデルも第99回は作成できず、第1〜3回から選ぶよう回答した。[範囲外のログ](logs/impl_invalid.txt)。第2回の指定ではLoRAについての問題が返った。[正常時のログ](logs/impl_valid.txt)。通常の文字列を返したため `[tool return]` としてモデルへ渡り、例外による `[tool error]` ではなかった。範囲外を例外にした比較は行っていない。

ローカルの追加テストを含む全テストは **23件成功**。Codespace側では教材の既存テスト **21件成功**（追加テストファイルはコピーしていない）。[Codespaceでのテスト](logs/pytest.txt)

### 発展：CodexのMCP設定と比較

調査日：2026年11月24日。実際に使用している Codex を選び、[公式MCPドキュメント](https://developers.openai.com/codex/mcp)と[設定の基本](https://developers.openai.com/codex/config-basic)を確認した。手元の `codex mcp add --help` でもコマンド起動と `--url` の選択肢を確認した。設定の変更や新規サーバーの登録は行っていない。

| 調べた点 | 第6回のエージェント | Codex |
|---|---|---|
| 設定場所 | プロジェクトの `app/mcp_servers.json` | 通常は `~/.codex/config.toml`、プロジェクト単位は `.codex/config.toml` |
| コマンドで起動 | JSONの `"command"` と `"args"` | TOMLの `[mcp_servers.名前]` に `command` と `args` |
| URLで接続 | JSONの `"url"` | TOMLの同じテーブルに `url`。CLIでは `codex mcp add 名前 --url URL` |
| 有効範囲 | このエージェントが読む設定 | ユーザー設定は共通、プロジェクト設定は信頼済みプロジェクトで有効 |

CodexでもMCPの接続先を追加できるが、演習のJSONをそのままCodexのTOML設定として読み込むわけではない。サーバー自身を変更せずに、対応する別のクライアントで利用できる点が共通している。

## 気づき

MCPを使うと、サーバー側で要点ツールを追加するだけでエージェントに新しいツールが見える。ツールから返る情報や説明文もモデルが使うため、提供元・公開先・返答の内容を確認することが重要だと分かった。利用できない講義回を指定された場合は、例外ではなく、次に指定できる回を示すことで回答につながった。
