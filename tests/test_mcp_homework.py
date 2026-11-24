"""追加したツールが MCP 経由で公開され、範囲外も文字列で返ることを確認。"""

from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.mcp_agent import build_mcp_agent
from app.mcp_server import make_quiz


def test_make_quiz_valid_and_invalid():
    assert "元の重みを固定" in make_quiz(2)
    assert "第1〜3回" in make_quiz(99)


def test_new_tools_are_published_and_return_error_message(tmp_path):
    from test_mcp_server import _glossary_only_config

    model = TestModel(call_tools=["glossary_make_quiz"])
    agent = build_mcp_agent(_glossary_only_config(tmp_path))
    result = agent.run_sync("クイズを作って", model=model)
    offered = {tool.name for tool in model.last_model_request_parameters.function_tools}
    assert {"glossary_get_lecture_summary", "glossary_make_quiz"} <= offered
    returns = [part for msg in result.all_messages() for part in msg.parts if isinstance(part, ToolReturnPart)]
    assert returns and "第1〜3回" in str(returns[0].content)
