import operator
from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, Self, TypeVar, Any

import pytest
from _pytest.outcomes import Skipped as SkippedException
from _pytest.skipping import xfailed_key, evaluate_xfail_marks

T_co = TypeVar('T_co', bound='Base')


def item_full_name(item: pytest.Item) -> str:
    return f'{item.module.__name__}.{item.name}'


@dataclass
class Case:
    name_pattern: str
    matcher: Callable[[str, str], bool] = operator.contains

    predicate: Callable[[], bool] | bool = True

    exception_types: list[type[Exception]] | type[Exception] = AssertionError
    exception_pattern: str = ''
    exception_matcher: Callable[[str, str], bool] = operator.contains

    def matched(self, name: str, exception: Exception | None = None) -> bool:
        try:
            return all((
                self.predicate() if callable(self.predicate) else self.predicate,
                self.matcher(name, self.name_pattern),
                isinstance(exception, self.exception_types) if exception is not None else True,
                self.exception_matcher(str(exception).strip("'"), self.exception_pattern) if exception is not None else True,
            ))
        except Exception as err:
            print(f'Exception in matched: {err}')
            return False


class Base:
    _register: list[Self]

    def __init__(self, items: Iterable[Case | str] | Case | str, marks: list[str | Any] | None = None):
        cases = []

        if isinstance(items, str):
            items = [Case(name_pattern=items)]

        if isinstance(items, Case):
            items = [items]

        for item in items:
            if isinstance(item, str):
                item = Case(name_pattern=item)
            cases.append(item)

        self.cases = cases
        self.marks = [] if marks is None else marks
        self._register.append(self)

    def __iter__(self):
        yield from self.cases

    @classmethod
    def matched(cls: type[T_co], item: pytest.Item, exception: Exception | None = None) -> Iterator[T_co]:
        name = item_full_name(item)
        yield from (cases for cases in cls._register if any(case.matched(name, exception) for case in cases))

    @classmethod
    def apply(cls, item: pytest.Item, exception: Exception | None = None):
        for cases in cls.matched(item, exception):
            for mark in cases.marks:
                item.add_marker(mark)


class Marked(Base):
    _register: list[Self] = []

    def __init__(self, *args, marks: list[str | Any], **kwargs):
        marks = [getattr(pytest.mark, mark) if isinstance(mark, str) else mark for mark in marks]
        super().__init__(*args, marks=marks, **kwargs)


class Uncollected(Base):
    _register: list[Self] = []


class Skipped(Marked):
    def __init__(self, *args, reason: str, **kwargs):
        super().__init__(*args, marks=[pytest.mark.skip(reason=reason)], **kwargs)


class XFailed(Marked):
    _register: list[Self] = []

    def __init__(self, *args, reason: str, **kwargs):
        super().__init__(*args, marks=[pytest.mark.xfail(reason=reason)], **kwargs)


def pytest_collection_modifyitems(config, items: list[pytest.Item]):
    selected = []
    for item in items:
        if any(Uncollected.matched(item)):
            continue
        selected.append(item)
        Marked.apply(item)

    items[:] = selected


@pytest.hookimpl(tryfirst=True, wrapper=True)
def pytest_runtest_makereport(item, call):
    if call.excinfo and call.excinfo.type is not SkippedException:
        XFailed.apply(item, call.excinfo.value)
        # breadcrumbs: _pytest/skipping.py:297 `xfailed = item.stash.get(xfailed_key, None)`
        item.stash[xfailed_key] = evaluate_xfail_marks(item)

    rep = yield

    return rep


def pytest_collection_finish(session):
    if session.config.option.collectonly:
        print('\n=== COLLECTED TESTS WITH MARKERS ===')
        for item in session.items:
            markers = [marker.name for marker in item.iter_markers()]
            print(f'{item.nodeid}')
            if markers:
                print(f'   Markers: {", ".join(markers)}')
            print()
