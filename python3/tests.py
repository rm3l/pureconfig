from .pure.parser import parse


def test_empty_line():
    line = ""

    # Try to parse it
    parse(line)


def test_single_line():
    line = "port = 8443"

    config = parse(line)

    assert config.get("port") == '8443'


def test_double_line():
    lines = "port = 8843\nbind = 0.0.0.0"

    config = parse(lines)

    assert config.get("port") == '8843'
    assert config.get("bind") == '0.0.0.0'
