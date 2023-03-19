import pytest
from text_chatgpt_connector import TCC


def test_set_key(caplog):
    caplog.set_level("DEBUG")
    tcc = TCC()

    caplog.clear()
    ret = tcc.set_key()
    assert not ret
    assert caplog.record_tuples == [
        ('text_chatgpt_connector.tcc', 40, 'Set OPEN_AI_API_KEY environment variable or use -k option'),
        ]

    caplog.clear()
    ret = tcc.set_key('test_key')
    assert ret
    assert caplog.record_tuples == []

    caplog.clear()
    ret = tcc.set_key()
    assert ret
    assert caplog.record_tuples == []


@pytest.mark.parametrize(
    'text, expected',
    [
        ('abc', 1),
        ('あいう', 2),
    ]
)
def test_get_size(text, expected):
    tcc = TCC()
    ret = tcc.get_size(text)
    assert ret == expected
