def validate_user_input(user_input: str) -> str:
    """
    Mirrors the validation rule used by the application:
    strip whitespace and reject empty input.
    """
    user_input = user_input.strip()

    if not user_input:
        raise ValueError("User message cannot be empty.")

    return user_input


def test_empty_input_is_rejected():
    try:
        validate_user_input("")
        assert False
    except ValueError:
        assert True


def test_whitespace_input_is_rejected():
    try:
        validate_user_input("   ")
        assert False
    except ValueError:
        assert True


def test_valid_input_is_accepted():
    result = validate_user_input("  Hello  ")

    assert result == "Hello"


def test_valid_input_is_trimmed():
    result = validate_user_input("   My name is Vipin.   ")

    assert result == "My name is Vipin."