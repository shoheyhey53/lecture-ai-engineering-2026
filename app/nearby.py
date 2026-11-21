"""検索ヒットと同じ資料の前後ページを、引用情報付きで追加する。"""


def expand_neighbors(hits: list[dict], pages: list[dict], radius: int = 1) -> list[dict]:
    """ヒットの順位を保ち、その後に未取得の隣接ページを加える。"""
    if radius < 0:
        raise ValueError("radius は 0 以上にしてください。")
    lookup = {(p["document_id"], p["page"]): p for p in pages}
    seen = set()
    results = []
    for hit in hits:
        if hit["page_id"] not in seen:
            seen.add(hit["page_id"])
            results.append({**hit, "retrieval_role": "search_hit"})
    for hit in hits:
        for offset in range(-radius, radius + 1):
            if not offset:
                continue
            page = lookup.get((hit["document_id"], hit["page"] + offset))
            if page and page["page_id"] not in seen:
                seen.add(page["page_id"])
                results.append({**page, "retrieval_role": "neighbor", "neighbor_of": hit["page_id"]})
    return results
