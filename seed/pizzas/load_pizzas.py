import json
from datetime import datetime, timezone
from pathlib import Path

from config.nosql import get_nosql_handle
from config.settings import settings


def normalize_pizza(raw_pizza):
    pizza_id = int(raw_pizza["id"])
    now = datetime.now(timezone.utc).isoformat()

    return {
        "id": pizza_id,
        "name": raw_pizza["name"],
        "description": raw_pizza["description"],
        "category": raw_pizza["category"],
        "price": float(raw_pizza["price"]),
        "image_name": raw_pizza["image_name"],
        "available": bool(raw_pizza["available"]),
        "created_at": now,
        "updated_at": now,
    }


def read_pizzas(file_path):
    with open(file_path, encoding="utf-8") as file:
        return [
            normalize_pizza(json.loads(line))
            for line in file
            if line.strip()
        ]


def load_pizzas():
    from borneo import PutRequest

    file_path = Path(
        settings.seed_path,
        "pizzas.jsonl",
    )

    pizzas = read_pizzas(file_path)
    handle = get_nosql_handle()

    try:
        request = PutRequest().set_table_name(settings.pizza_table_name)

        for pizza in pizzas:
            request.set_value(pizza)
            handle.put(request)
            print(f"Loaded pizza {pizza['id']}")

        print("Pizza data loaded")
    finally:
        handle.close()
