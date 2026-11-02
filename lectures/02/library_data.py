# 第2回 実装：架空の「まちの図書室」の FAQ
FAQ = {
    "hours": "開室日は火曜から土曜で、時間は10時から18時です。",
    "loan": "本は一人3冊まで、14日間借りられます。",
    "place": "図書室は駅前市民センターの2階にあります。",
    "renewal": "貸出期間の延長は返却期限内に1回だけ手続きできます。",
    "return": "返却は図書室入口の赤い返却ボックスに入れてください。",
}
FAQ_TEXT = "\n".join(f"- {v}" for v in FAQ.values())
GROUNDED = {
    "hours": (["何時に開きますか", "開室日と開室時間を教えてください", "図書室の開室日はいつですか", "週末の開室時間は？"], ["10時", "18時"]),
    "loan": (["何冊借りられますか", "貸出できる冊数と期間は", "本はいつまで借りられますか", "貸出の上限冊数と日数は？"], ["3冊", "14日"]),
    "place": (["図書室はどこですか", "建物と階を教えてください", "センターの何階ですか", "図書室がある場所は？"], ["駅前市民センター", "2階"]),
    "renewal": (["貸出期間の延長はできますか", "期限延長の条件は何ですか", "貸出延長の回数は？", "何回までいつ延長できますか"], ["期限内", "1回"]),
    "return": (["本はどこに返しますか", "返却方法を教えてください", "返却ボックスの場所はどこですか", "本を返す箱の色と場所は？"], ["入口", "赤い"]),
}
UNGROUNDED = [
    "予約はできますか", "利用カードの発行に料金はかかりますか", "貸出の予約は何冊できますか",
    "図書室で飲食できますか", "返却期限を過ぎると罰金はありますか", "Wi-Fiは使えますか",
    "本を郵送で返却できますか", "館内にコピー機はありますか",
]
TEST_EXTRA_GROUNDED = {
    "hours": ["開室時間を始まりから終わりまで教えてください", "何時から何時まで利用できますか"],
    "loan": ["本を借りられる冊数と日数を答えてください", "貸出は最大何冊で何日間ですか"],
    "place": ["図書室はどの建物の何階ですか", "駅前の図書室の所在地を教えてください"],
    "renewal": ["借りた本は期限内に何回延長できますか", "貸出期限を延長する条件を教えてください"],
    "return": ["本を返す場所と箱の色を教えてください", "返却用の赤い箱はどこですか"],
}
TEST_EXTRA_UNGROUNDED = [
    "子ども向けの読み聞かせはありますか", "本を取り寄せることはできますか",
    "臨時休室はいつですか", "図書室に駐車場はありますか",
]

UNGROUNDED_ANSWER = "この FAQ には記載がありません。運営に確認が必要です。"

def make_example(question: str, answer: str, needs_review: bool) -> dict:
    target = json.dumps({"answer": answer, "needs_review": needs_review}, ensure_ascii=False)
    return {"question": question, "faq": FAQ_TEXT, "target": target, "needs_review": needs_review}

def split_templates(templates):
    # テンプレートの先頭 2 つを train、3 つ目を valid、4 つ目を test に固定（言い換えを跨がせない）
    return templates[:2], templates[2:3], templates[3:4]

train, valid, test, gold = [], [], [], {}
for key, (templates, must_include) in GROUNDED.items():
    tr, va, te = split_templates(templates)
    for q in tr: train.append(make_example(q, FAQ[key], False))
    for q in va: valid.append(make_example(q, FAQ[key], False))
    for q in te + TEST_EXTRA_GROUNDED[key]:
        test.append(make_example(q, FAQ[key], False)); gold[q] = {"needs_review": False, "must_include": must_include}
for i, q in enumerate(UNGROUNDED):
    ex = make_example(q, UNGROUNDED_ANSWER, True)
    bucket = [train, train, valid, test][i % 4]   # 根拠なしの質問は 4 問ごとに train 2 / valid 1 / test 1 に振る
    bucket.append(ex)
    if bucket is test: gold[q] = {"needs_review": True, "must_include": ["確認"]}
for q in TEST_EXTRA_UNGROUNDED:
    test.append(make_example(q, UNGROUNDED_ANSWER, True)); gold[q] = {"needs_review": True, "must_include": ["確認"]}

# train は 14 件（根拠あり 10、根拠なし 4）。同じ例を何回学習するかは、データを複製せず、セクション 4 の num_train_epochs で決める
all_questions = [r["question"] for r in train + valid + test]
assert len(set(all_questions)) == len(all_questions), "質問が train / valid / test のどこかで重複しています。テンプレートを見直してください"
print(f"train={len(train)} valid={len(valid)} test={len(test)} gold={len(gold)}")
print("学習例の 1 件 | 質問:", train[0]["question"], "| 望ましい出力:", train[0]["target"])
_ = (WORK / "train.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in train), encoding="utf-8")
_ = (WORK / "test.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in test), encoding="utf-8")
_ = (WORK / "gold.json").write_text(json.dumps(gold, ensure_ascii=False, indent=2), encoding="utf-8")
