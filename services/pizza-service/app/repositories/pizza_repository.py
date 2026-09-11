from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Protocol

from oci.exceptions import ServiceError
from oci.nosql import NosqlClient
from oci.nosql.models import QueryDetails, UpdateRowDetails

from app.config.settings import Settings
from app.models.pizza_model import Pizza


class PizzaRepository(Protocol):
    def list_available(self) -> List[Pizza]:
        pass

    def get_by_id(self, pizza_id: int) -> Optional[Pizza]:
        pass

    def create(self, pizza: Pizza) -> Pizza:
        pass

    def update(self, pizza_id: int, values: Dict[str, object]) -> Optional[Pizza]:
        pass

    def delete(self, pizza_id: int) -> bool:
        pass


class NoSqlPizzaRepository:
    def __init__(self, client: NosqlClient, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    def list_available(self) -> List[Pizza]:
        statement = (
            f"SELECT * FROM {self.settings.nosql_table} "
            "WHERE available = true"
        )
        pizzas: List[Pizza] = []
        page: Optional[str] = None

        while True:
            kwargs = {"page": page} if page is not None else {}
            result = self.client.query(
                QueryDetails(
                    compartment_id=self.settings.nosql_compartment_id,
                    statement=statement,
                ),
                **kwargs,
            )
            pizzas.extend(self._to_pizza(item) for item in result.data.items)

            page = getattr(result, "next_page", None)
            if page is None:
                return pizzas

    def get_by_id(self, pizza_id: int) -> Optional[Pizza]:
        try:
            result = self.client.get_row(
                self.settings.nosql_table,
                self._key(pizza_id),
                compartment_id=self.settings.nosql_compartment_id,
            )
        except ServiceError as exc:
            if exc.status == 404:
                return None

            raise

        if result.data.value is None:
            return None

        return self._to_pizza(result.data.value)

    def create(self, pizza: Pizza) -> Pizza:
        if pizza.id == 0:
            pizza.id = self._next_id()

        self.client.update_row(
            self.settings.nosql_table,
            UpdateRowDetails(
                compartment_id=self.settings.nosql_compartment_id,
                value=pizza.model_dump(mode="json"),
                option="IF_ABSENT",
            ),
        )

        return pizza

    def _next_id(self) -> int:
        statement = f"SELECT id FROM {self.settings.nosql_table}"
        result = self.client.query(
            QueryDetails(
                compartment_id=self.settings.nosql_compartment_id,
                statement=statement,
            )
        )
        ids = [int(item["id"]) for item in result.data.items]
        return max(ids, default=0) + 1

    def update(self, pizza_id: int, values: Dict[str, object]) -> Optional[Pizza]:
        pizza = self.get_by_id(pizza_id)

        if pizza is None:
            return None

        updated = pizza.model_copy(
            update={
                **values,
                "updated_at": datetime.now(timezone.utc),
            }
        )

        self.client.update_row(
            self.settings.nosql_table,
            UpdateRowDetails(
                compartment_id=self.settings.nosql_compartment_id,
                value=updated.model_dump(mode="json"),
                option="IF_PRESENT",
            ),
        )

        return updated

    def delete(self, pizza_id: int) -> bool:
        try:
            result = self.client.delete_row(
                self.settings.nosql_table,
                self._key(pizza_id),
                compartment_id=self.settings.nosql_compartment_id,
            )
        except ServiceError as exc:
            if exc.status == 404:
                return False

            raise

        return bool(result.data.is_success)

    def _key(self, pizza_id: int) -> List[str]:
        return [f"id:{pizza_id}"]

    def _to_pizza(self, value: Dict[str, object]) -> Pizza:
        return Pizza.model_validate(value)


class LocalNoSqlPizzaRepository:
    def __init__(self, handle, table_name: str) -> None:
        self.handle = handle
        self.table_name = table_name

    def list_available(self) -> List[Pizza]:
        from borneo import QueryRequest

        request = QueryRequest().set_statement(
            f"SELECT * FROM {self.table_name} WHERE available = true"
        )
        pizzas: List[Pizza] = []

        while True:
            result = self.handle.query(request)
            pizzas.extend(self._to_pizza(item) for item in result.get_results())

            if request.is_done():
                return pizzas

    def get_by_id(self, pizza_id: int) -> Optional[Pizza]:
        from borneo import GetRequest

        result = self.handle.get(
            GetRequest()
            .set_table_name(self.table_name)
            .set_key({"id": pizza_id})
        )
        value = result.get_value()

        if value is None:
            return None

        return self._to_pizza(value)

    def create(self, pizza: Pizza) -> Pizza:
        from borneo import PutOption, PutRequest

        if pizza.id == 0:
            pizza.id = self._next_id()

        self.handle.put(
            PutRequest()
            .set_table_name(self.table_name)
            .set_value(pizza.model_dump(mode="json"))
            .set_option(PutOption.IF_ABSENT)
        )

        return pizza

    def _next_id(self) -> int:
        from borneo import QueryRequest

        request = QueryRequest().set_statement(
            f"SELECT id FROM {self.table_name}"
        )
        ids = []

        while True:
            result = self.handle.query(request)
            ids.extend(int(item["id"]) for item in result.get_results())

            if request.is_done():
                return max(ids, default=0) + 1

    def update(self, pizza_id: int, values: Dict[str, object]) -> Optional[Pizza]:
        from borneo import PutOption, PutRequest

        pizza = self.get_by_id(pizza_id)

        if pizza is None:
            return None

        updated = pizza.model_copy(
            update={
                **values,
                "updated_at": datetime.now(timezone.utc),
            }
        )

        self.handle.put(
            PutRequest()
            .set_table_name(self.table_name)
            .set_value(updated.model_dump(mode="json"))
            .set_option(PutOption.IF_PRESENT)
        )

        return updated

    def delete(self, pizza_id: int) -> bool:
        from borneo import DeleteRequest

        result = self.handle.delete(
            DeleteRequest()
            .set_table_name(self.table_name)
            .set_key({"id": pizza_id})
        )

        return result.get_success()

    def _to_pizza(self, value: Dict[str, object]) -> Pizza:
        return Pizza.model_validate(value)


class InMemoryPizzaRepository:
    """
    Implementação isolada para testes automatizados.
    """

    def __init__(self) -> None:
        self._pizzas: Dict[int, Pizza] = {}

    def list_available(self) -> List[Pizza]:
        return [pizza for pizza in self._pizzas.values() if pizza.available]

    def get_by_id(self, pizza_id: int) -> Optional[Pizza]:
        return self._pizzas.get(pizza_id)

    def create(self, pizza: Pizza) -> Pizza:
        if pizza.id == 0:
            pizza.id = max(
                (stored.id for stored in self._pizzas.values()),
                default=0,
            ) + 1

        self._pizzas[pizza.id] = pizza
        return pizza

    def update(self, pizza_id: int, values: Dict[str, object]) -> Optional[Pizza]:
        pizza = self.get_by_id(pizza_id)

        if pizza is None:
            return None

        updated = pizza.model_copy(
            update={
                **values,
                "updated_at": datetime.now(timezone.utc),
            }
        )

        self._pizzas[pizza_id] = updated

        return updated

    def delete(self, pizza_id: int) -> bool:
        if pizza_id not in self._pizzas:
            return False

        del self._pizzas[pizza_id]

        return True
