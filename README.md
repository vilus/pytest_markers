pytest "плагин" для установки меток (в том числе skip, xfail),

можно задать несколько меток нескольким кейсам,

можно задавать кастомную фильтрацию по имени кейсов, для XFail еще можно фильтровать по типу и тексту исключения,

можно исключить кейсы из "собранных" (`collected`),

примеры в `tests/test_marks.py`, вот некоторые из них,

 - выставление нескольких меток (одна с параметром) с фильтрацией имени по регулярке:
```python
Marked(
    items=[Case(
        name_pattern=r'_and_matcher$',
        matcher=lambda msg, pattern: bool(re.search(pattern, msg)),
    )],
    marks=['matched', pytest.mark.a_native_mark(some_param='qwerty')]
)


def test_marked_by_predicate_and_matcher():
    # pytest -vv -s --collect-only -m "a_native_mark(some_param='qwerty')"
    pass
```

- выставление `xfail` с фильтрацией по типу и тексту исключения:
```python
XFailed(
    items=[Case(
        name_pattern='xfail',
        exception_types=KeyError,
        exception_pattern='y_1234567890',
        exception_matcher=lambda msg, pattern: msg.endswith(pattern),
    )],
    reason='xfailed by plugin testing, catch by exception type with exception_matcher'
)


def test_xfailed_by_ecx_type_and_exception_mather():
    raise KeyError('one qwerty_1234567890')


def test_xfailed_by_ecx_type_and_exception_mather_two():
    raise KeyError('two tooty_1234567890')
```

- исключение кейса из "собранных" с фильтрацией по предикату:
```python
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
```

- несколько меток на несколько кейсов:
```python
Marked(
    items=[
        'simple_marked',
        Case(name_pattern='no_marked_by_p'),
    ],
    marks=['marked_1', 'marked_2']
)


def test_simple_marked():
    # pytest -s -vv --collect-only
    pass


def test_no_marked_by_predicate():
    pass
```



- [ ] TODO: сделать "устанавливаемым" через `pip`
