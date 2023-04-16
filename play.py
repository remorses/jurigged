import re
import select
import sys
import termios
import traceback
import tty
from contextlib import contextmanager
from functools import partial


ANSI_ESCAPE = re.compile(r"\x1b\[[;\d]*[A-Za-z]")
ANSI_ESCAPE_INNER = re.compile(r"[\x1b\[;\d]")
ANSI_ESCAPE_END = re.compile(r"[A-Za-z~]")

def read_chars():
    return
    esc = None
    try:
        while True:
            ready, _, _ = select.select([sys.stdin], [], [], 0.02)
            if ready:
                # Sometimes, e.g. when pressing an up arrow, multiple
                # characters are buffered, and read1() is the only way
                # I found to read precisely what was buffered. select
                # seems unreliable in these cases, probably because the
                # buffer fools it into thinking there is nothing else
                # to read. So read(1) would leave some characters dangling
                # in the buffer until the next keypress.
                for ch in sys.stdin.buffer.read1():
                    ch = chr(ch)
                    if esc is not None:
                        if ANSI_ESCAPE_INNER.match(ch):
                            esc += ch
                        elif ANSI_ESCAPE_END.match(ch):
                            yield {"char": esc + ch, "escape": True}
                            esc = None
                        else:
                            yield {"char": esc, "escape": True}
                            esc = None
                            yield {"char": ch}
                    elif ch == "\x1b":
                        esc = ""
                    else:
                        yield {"char": ch}
    except:
        pass

tty.setcbreak(sys.stdin)

for ch in read_chars():
    print(ch)