from nidaqmx_on_pi import greet


def test_greet():
    assert greet("Alice") == "Hello, Alice"
