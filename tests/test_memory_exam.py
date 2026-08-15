from memory.conversation_memory import ConversationMemoryManager


def test_memory_exam_state_initialization():
    memory = ConversationMemoryManager(
        max_turns=10,
        max_tokens=1000,
    )

    memory.add_user_message(
        "My name is Vipin."
    )

    memory.add_assistant_message(
        "Nice to meet you, Vipin."
    )

    history = memory.get_sliding_window_history()

    assert any(
        message["content"] == "My name is Vipin."
        for message in history
    )


def test_memory_exam_context_survives_distraction():
    memory = ConversationMemoryManager(
        max_turns=10,
        max_tokens=1000,
    )

    # State initialization
    memory.add_user_message(
        "My name is Vipin."
    )
    memory.add_assistant_message(
        "Nice to meet you, Vipin."
    )

    # Context distraction
    for i in range(1, 6):
        memory.add_user_message(
            f"Tell me something about topic {i}."
        )
        memory.add_assistant_message(
            f"Here is information about topic {i}."
        )

    history = memory.get_sliding_window_history()

    # State extraction:
    # The original name should still be present because
    # the conversation has not exceeded the configured window.
    contents = [
        message["content"]
        for message in history
    ]

    assert "My name is Vipin." in contents
    assert "Nice to meet you, Vipin." in contents


def test_memory_exam_fifo_removes_old_state_when_window_is_exceeded():
    memory = ConversationMemoryManager(
        max_turns=3,
        max_tokens=1000,
    )

    # Initial state
    memory.add_user_message(
        "My name is Vipin."
    )
    memory.add_assistant_message(
        "Nice to meet you, Vipin."
    )

    # Add enough turns to exceed the 3-turn window.
    for i in range(1, 5):
        memory.add_user_message(
            f"Distraction question {i}"
        )
        memory.add_assistant_message(
            f"Distraction answer {i}"
        )

    history = memory.get_sliding_window_history()

    contents = [
        message["content"]
        for message in history
    ]

    # The oldest state should have been pruned.
    assert "My name is Vipin." not in contents
    assert "Nice to meet you, Vipin." not in contents

    # The newest complete turns should remain.
    assert "Distraction question 4" in contents
    assert "Distraction answer 4" in contents


def test_memory_exam_preserves_complete_pairs():
    memory = ConversationMemoryManager(
        max_turns=3,
        max_tokens=1000,
    )

    for i in range(1, 6):
        memory.add_user_message(
            f"Question {i}"
        )
        memory.add_assistant_message(
            f"Answer {i}"
        )

    history = memory.get_sliding_window_history()

    # Every retained user message should be followed
    # by its corresponding assistant message.
    assert len(history) % 2 == 0

    for index in range(0, len(history), 2):
        assert history[index]["role"] == "user"
        assert history[index + 1]["role"] == "assistant"