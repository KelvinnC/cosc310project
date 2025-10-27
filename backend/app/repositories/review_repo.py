from pathlib import Path
import json
from typing import Dict, Any, Iterator

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews.json"


def iter_all(chunk_size: int = 1 << 20, _shrink_threshold: int = 1 << 19) -> Iterator[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return
    try:
        import ijson
        with DATA_PATH.open("rb") as f:
            yield from ijson.items(f, "item")
        return
    except ImportError:
        pass

    decoder = json.JSONDecoder()
    buf = ""
    idx = 0

    with DATA_PATH.open("r", encoding="utf-8-sig") as f:
        while True:
            if idx < len(buf):
                ch = buf[idx]
            else:
                more = f.read(chunk_size)
                if not more:
                    return
                buf += more
                continue

            if ch.isspace():
                idx += 1
                continue
            if ch == "[":
                idx += 1
                break
            return

        while True:
            while True:
                if idx < len(buf):
                    ch = buf[idx]
                    if ch.isspace() or ch == ",":
                        idx += 1
                        continue
                    break
                more = f.read(chunk_size)
                if not more:
                    return
                buf += more

            if ch == "]":
                return

            while True:
                try:
                    item, end = decoder.raw_decode(buf, idx)
                    yield item
                    idx = end
                    if idx > _shrink_threshold:
                        buf = buf[idx:]
                        idx = 0
                    break
                except json.JSONDecodeError:
                    more = f.read(chunk_size)
                    if not more:
                        raise
                    buf += more
