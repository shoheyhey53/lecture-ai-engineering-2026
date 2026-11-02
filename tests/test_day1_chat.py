from types import SimpleNamespace

from app.ask import chat_loop


def test_chat_keeps_one_session_and_ignores_blank(capsys):
    class Chat:
        def __init__(self):
            self.messages = []

        def send_message(self, message):
            self.messages.append(message)
            return SimpleNamespace(text=f"返答{len(self.messages)}", usage_metadata=None)

    chat = Chat()
    creations = []

    def create(*, model):
        creations.append(model)
        return chat

    client = SimpleNamespace(chats=SimpleNamespace(create=create))
    messages = iter(["名前はポチ", "", "名前は？", "/quit"])
    chat_loop(client, input_fn=lambda _: next(messages))
    assert len(creations) == 1
    assert chat.messages == ["名前はポチ", "名前は？"]
    assert "返答2" in capsys.readouterr().out


def test_chat_ends_on_eof(capsys):
    client = SimpleNamespace(chats=SimpleNamespace(create=lambda **_: object()))
    def end(_):
        raise EOFError
    chat_loop(client, input_fn=end)
    assert "対話を終了" in capsys.readouterr().out
