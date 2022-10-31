import pathlib
from typing import Iterable


class ParserError(Exception):
    pass


def _read_words(path: pathlib.Path) -> Iterable[str]:
    with path.open() as f:
        line_num: int
        line: str
        for line_num, line in enumerate(f):
            line = line.strip()
            if line == '':
                continue
            if (line_words := len(line.split())) > 1:
                raise ParserError(f'{path} line {line_num + 1}: Expected a single word per line, found {line_words}')
            if (word_len := len(line)) < 2:
                raise ParserError(f'{path} line {line_num + 1}: Expected words of length >= 2, found {word_len}')
            yield line


def parse_words_file(path: str) -> frozenset[str]:
    path: pathlib.Path = pathlib.Path(path)
    if not path.is_file():
        raise ParserError(f'"{path}" is not a valid path')
    return frozenset(_read_words(path))
