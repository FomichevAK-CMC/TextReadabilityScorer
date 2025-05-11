from typing import TextIO, List
import re, tempfile


class ReadBuffer:
    """Sliding window buffer for memory-safe reading from text file"""
    def __init__(self, file: TextIO, size: int = 4096):
        self.size = size
        self.file = file
        self.str = ''
        self.next()

    def next(self, n: int = -1) -> bool:
        """Load next n characters from file into buffer.
        If n < 0 it will try to load the same number of characters as the buffer size.
        Returns False if the buffer is empty after this operation.
        """
        if n < 0:
            n = self.size
        if n > 0:
            self.str = self.str[n:] + self.file.read(n)
        return self.__bool__()

    def __bool__(self):
        return len(self.str) != 0


class TType:
    def __init__(self, tag: str = None, subtag: str = None):
        self.tag = tag
        self.subtag = subtag

    def __eq__(self, other):
        return self.tag == other.tag and self.subtag == other.subtag


class Token(TType):
    def __init__(self, tag: str = None, subtag: str = None, body: str = ''):
        super().__init__(tag, subtag)
        self.body = body

    def __len__(self):
        return len(self.body)

    def __repr__(self):
        return f"""<{f"'{self.tag}'" if self.tag else None}, {f"'{self.subtag}'" if self.subtag else None}, {repr(self.body)}>"""


class TModel(TType):
    def __init__(self, tag: str = None, subtag: str = None, regex: str = None):
        super().__init__(tag, subtag)
        self.regex = re.compile(regex) if regex else None

    def test(self, text: str) -> str:
        """Returns string that matched the model regex.
        If text did not match, returns empty string.
        """
        if m := self.regex.match(text):
            return m.group(0)
        return ""

    def __repr__(self):
        return f"<'{self.tag}', '{self.subtag}', '{self.regex}'>"


class TList(list):
    def filter(self, types: List[TType], remove: bool = True):
        """If remove == True, returns TList with all Tokens with given types removed.
        If remove == False, returns TList of all and only the Tokens with givens types.
        """
        return TList(filter(lambda t: (t in types) ^ remove, self))

    def split(self, types: List[TType], keep_sep: bool = True, rev: bool = False) -> List:
        """Returns a List[TList] by splitting original TList with Tokens of given types as separators."""
        res = []
        seq = TList()
        for t in (self if not rev else reversed(self)):
            if t not in types:
                seq.append(t)
            else:
                if keep_sep:
                    seq.append(t)
                res.append(seq)
                seq = TList()
        return res if not rev else reversed(res)

    def join(self, sep: str = ' ') -> str:
        if len(self) == 0:
            return ''
        elif isinstance(self[0], Token):
            return sep.join(t.body for t in self)
        else:
            return ''


def scan_file(file: TextIO | str, models: List[TModel], *, stop: List[TModel] = (), skip_unmatched: bool = False, max_token_len: int = 4096) -> TList:
    """Scans text file and generates TList of all matched Tokens.
    if skip_unmatched == False, and <substring> failed to match with any of the rules,
    Token with None tag and None subtag is generated with the <substring> as a body.
    """
    buf = ReadBuffer(file, max_token_len)
    tokens = TList()
    unmatched = ""
    while buf:
        for m in models:
            if t := m.test(buf.str):
                if not skip_unmatched and unmatched:
                    tokens.append(Token(body=unmatched))
                    unmatched = ""
                tkn = Token(m.tag, m.subtag, t)
                if tkn not in stop:
                    tokens.append(tkn)
                buf.next(len(t))
                break
        else:
            if not skip_unmatched:
                unmatched += buf.str[0]
            buf.next(1)

    if not skip_unmatched and unmatched:
        tokens.append(Token(body=unmatched))
    return tokens


def scan_text(text: str, models: List[TModel], *, stop: List[TModel] = (), skip_unmatched: bool = False, max_token_len: int = 4096) -> TList:
    with tempfile.TemporaryFile('w+') as tmp:
        tmp.write(text)
        tmp.seek(0)
        return scan_file(tmp, models, stop=stop, skip_unmatched=skip_unmatched, max_token_len=max_token_len)