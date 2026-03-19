from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://db.ygoprodeck.com/api/v7/cardinfo.php"


def fetch_card(name: str) -> dict[str, object]:
    query = urlencode({"name": name})
    request = Request(
        f"{API_BASE}?{query}",
        headers={"User-Agent": "duel-master-card-fetch/1.0"},
    )
    with urlopen(request) as response:  # noqa: S310
        payload = json.load(response)

    card = payload["data"][0]
    return {
        "source": "YGOPRODeck API v7",
        "name": card["name"],
        "id": card["id"],
        "type": card["type"],
        "desc": card["desc"],
        "atk": card.get("atk"),
        "def": card.get("def"),
        "level": card.get("level"),
        "race": card.get("race"),
        "attribute": card.get("attribute"),
    }


def main() -> int:
    card = fetch_card("Blue-Eyes White Dragon")
    print(json.dumps(card, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
