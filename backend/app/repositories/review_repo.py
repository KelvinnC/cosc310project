from pathlib import Path
import json
from typing import Dict, Any, Iterator, List

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews.json"


def _stream_items(chunk_size: int = 1 << 20, _shrink_threshold: int = 1 << 19) -> Iterator[Dict[str, Any]]:
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


def list_page(page: int, per_page: int) -> List[Dict[str, Any]]:
    if page < 1:
        raise ValueError("page must be >= 1")
    if per_page < 1:
        raise ValueError("per_page must be >= 1")
    start = (page - 1) * per_page
    end = start + per_page

    items: List[Dict[str, Any]] = []
    for idx, item in enumerate(_stream_items()):
        if idx < start:
            continue
        if idx >= end:
            break
        items.append(item)
    return items


def iter_pages(per_page: int) -> Iterator[List[Dict[str, Any]]]:
    if per_page < 1:
        raise ValueError("per_page must be >= 1")
    page: List[Dict[str, Any]] = []
    for item in _stream_items():
        page.append(item)
        if len(page) >= per_page:
            yield page
            page = []
    if page:
        yield page
