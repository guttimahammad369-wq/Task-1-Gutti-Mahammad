from memory.conversation_memory import ConversationMemoryManager


def test_user_assistant_messages_are_stored():
    memory = ConversationMemoryManager(
        max_turns=10,
        max_tokens=1000,
    )

    memory.add_user_message("Hello")
    memory.add_assistant_message("Hi there")

    history = memory.get_sliding_window_history()

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there"


def test_fifo_pruning_keeps_latest_complete_turns():
    memory = ConversationMemoryManager(
        max_turns=3,
        max_tokens=100000,
    )

    for i in range(1, 6):
        memory.add_user_message(f"user message {i}")
        memory.add_assistant_message(f"assistant message {i}")

    history = memory.get_sliding_window_history()

    assert len(history) == 6

    assert history[0]["content"] == "user message 3"
    assert history[1]["content"] == "assistant message 3"

    assert history[2]["content"] == "user message 4"
    assert history[3]["content"] == "assistant message 4"

    assert history[4]["content"] == "user message 5"
    assert history[5]["content"] == "assistant message 5"


def test_token_pruning_preserves_complete_pairs():
    memory = ConversationMemoryManager(
        max_turns=100,
        max_tokens=50,
    )

    for _ in range(5):
        memory.add_user_message("U" * 40)
        memory.add_assistant_message("A" * 40)

    history = memory.get_sliding_window_history()

    # Each message is approximately 10 tokens.
    # One complete pair is approximately 20 tokens.
    # 50-token budget therefore permits two complete pairs.
    assert len(history) == 4

    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert history[2]["role"] == "user"
    assert history[3]["role"] == "assistant"

    active_tokens = sum(
        memory.estimate_tokens(
            message["content"]
        )
        for message in history
    )

    assert active_tokens <= 50


def test_session_id_is_created():
    memory = ConversationMemoryManager()

    assert memory.session_id
    assert memory.thread.session_id == memory.session_id


def test_clear_memory_removes_messages():
    memory = ConversationMemoryManager()

    memory.add_user_message("Hello")
    memory.add_assistant_message("Hi")

    assert len(memory.thread.messages) == 2

    memory.clear_memory()

    assert len(memory.thread.messages) == 0
    assert memory.get_sliding_window_history() == []