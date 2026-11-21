from app.nearby import expand_neighbors


def page(doc, number):
    return {"page_id": f"{doc}-{number}", "document_id": doc, "page": number,
            "content": f"本文{number}", "title": "title", "lecture": 1}


def test_neighbors_preserve_hits_and_do_not_cross_documents():
    pages = [page("a", n) for n in (1, 2, 3, 4)] + [page("b", 1)]
    hits = [{**pages[1], "distance": 0.1}, {**pages[2], "distance": 0.2}]
    result = expand_neighbors(hits, pages)
    assert [p["page_id"] for p in result] == ["a-2", "a-3", "a-1", "a-4"]
    assert result[0]["distance"] == 0.1
    assert result[2]["neighbor_of"] == "a-2"
    assert "distance" not in result[2]


def test_radius_zero_and_negative():
    import pytest

    hits = [page("a", 1)]
    assert len(expand_neighbors(hits, hits, radius=0)) == 1
    with pytest.raises(ValueError):
        expand_neighbors(hits, hits, radius=-1)


def test_search_tool_expands_actual_search_results(monkeypatch):
    import json
    from app import retrieval, tools

    pages = [page("a", n) for n in (1, 2, 3)]
    monkeypatch.setattr(retrieval, "search", lambda query: [{**pages[1], "distance": 0.1}])
    monkeypatch.setattr(retrieval, "load_pages", lambda: pages)
    results = json.loads(tools.search_materials_neighbors("example"))["results"]
    assert [p["page_id"] for p in results] == ["a-2", "a-1", "a-3"]


def test_graph_multi_prioritizes_seeds_and_records_query_provenance(monkeypatch):
    from app import retrieval

    def fake_graph(query):
        if query == "first":
            return {"seeds": [page("a", 1)], "expanded": [page("a", 3)]}
        return {"seeds": [page("a", 2)], "expanded": [page("a", 3)]}

    monkeypatch.setattr(retrieval, "search_graph", fake_graph)
    result = retrieval.search_graph_multi(["first", "second"])
    assert [p["page_id"] for p in result["results"]] == ["a-1", "a-2", "a-3"]
    assert result["results"][2]["queries"] == ["first", "second"]


def test_graph_multi_rejects_empty_or_excess_queries():
    import pytest
    from app.retrieval import search_graph_multi

    for queries in ([], [""], ["a", "b", "c", "d"]):
        with pytest.raises(ValueError):
            search_graph_multi(queries)
