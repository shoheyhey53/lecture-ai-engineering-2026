import json

import pytest
from pydantic_ai import DeferredToolRequests, DeferredToolResults
from pydantic_ai.models.test import TestModel

from app import tools
from app.agent import agent


def test_quiz_uses_requested_lecture_and_handles_unknown():
    result = json.loads(tools.make_quiz(2))
    terms = [term for term in tools.load_glossary() if term['lecture'] == 2]
    assert any(item['term'] in result['question'] and item['definition'] == result['answer'] for item in terms)
    assert '見つかりません' in tools.make_quiz(0)


@pytest.mark.parametrize('approve', [False, True])
def test_learning_log_needs_approval(tmp_path, monkeypatch, approve):
    monkeypatch.setattr(tools, '__file__', str(tmp_path / 'app' / 'tools.py'))
    model = TestModel(call_tools=['save_learning_log'])
    pending = agent.run_sync('学習記録を保存する', model=model)
    assert isinstance(pending.output, DeferredToolRequests)
    assert len(pending.output.approvals) == 1
    directory = tmp_path / 'learning_log'
    assert not directory.exists()
    call = pending.output.approvals[0]
    results = DeferredToolResults(approvals={call.tool_call_id: approve})
    agent.run_sync(message_history=pending.all_messages(), deferred_tool_results=results, model=model)
    assert directory.exists() is approve
    if approve:
        files = list(directory.glob('*.json'))
        assert len(files) == 1
        assert 'content' in json.loads(files[0].read_text(encoding='utf-8'))
