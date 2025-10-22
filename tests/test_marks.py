import re

import pytest

from marks import Marked, Skipped, XFailed, Uncollected, Case


Marked(
    items=[
        'simple_marked',
        Case(name_pattern='no_marked_by_p'),
    ],
    marks=['marked_1', 'marked_2']
)
Marked(items=[], marks=['should_not_be'])
Marked(items=[Case(name_pattern='no_marked_by_predicate', predicate=False)], marks=['should_not_be'])
Marked(items=[Case(name_pattern='no_marked_by_predicate', predicate=lambda: False)], marks=['should_not_be'])
Marked(
    items=[Case(
        name_pattern=r'_and_matcher$',
        matcher=lambda msg, pattern: bool(re.search(pattern, msg)),
        predicate=True,
    )],
    marks=['matched', pytest.mark.a_native_mark(some_param='qwerty')]
)


def test_simple_marked():
    # pytest -s -vv --collect-only
    pass


def test_no_marked_by_predicate():
    pass


def test_marked_by_predicate_and_matcher():
    # pytest -vv -s --collect-only -m "a_native_mark(some_param='qwerty')"
    pass


# ---
Skipped(items=['test_skipped'], reason='skipped by plugin testing')


def test_skipped():
    pass


# ---
# длинные сообщения `reason`, вывод обрезается, поэтому: `pytest -s -vv`
XFailed(items=['simple_xfail'], reason='xfailed by plugin testing')
XFailed(
    items=[Case(name_pattern='xfail', exception_pattern='catch XFail by exception m')],
    reason='xfailed by plugin testing, catch by exception message'
)
XFailed(
    items=[Case(
        name_pattern='xfail',
        exception_types=KeyError,
        exception_pattern='y_1234567890',
        exception_matcher=lambda msg, pattern: msg.endswith(pattern),
    )],
    reason='xfailed by plugin testing, catch by exception type with exception_matcher'
)


def test_simple_xfailed():
    assert False, 'For catch XFail'


def test_xfailed_by_exc_msg():
    assert False, 'For catch XFail by exception message'


def test_xfailed_by_ecx_type_and_exception_mather():
    raise KeyError('one qwerty_1234567890')


def test_xfailed_by_ecx_type_and_exception_mather_two():
    raise KeyError('two tooty_1234567890')


# ---
Uncollected(items=[
    Case(
        name_pattern='uncollected',
        # between `1.1.8` and `1.1.45'
        predicate=lambda: bool(re.search(r'1.1.(4[0-5]|[1-3][0-9]|[8-9]){1,2}($|-)', '1.1.42-003'))
    ),
])


def test_uncollected():
    # pytest -vv -s -k "test_uncollected"
    # pytest -vv -s --collect-only -k "test_uncollected"
    # pytest -vv -s --collect-only
    pass
