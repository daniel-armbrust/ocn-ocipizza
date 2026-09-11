from config.nosql import get_nosql_handle
from config.settings import settings


def create_tables():
    from borneo import TableLimits, TableRequest

    table_name = settings.pizza_table_name

    drop_statement = f"DROP TABLE IF EXISTS {table_name}"

    create_statement = (
        f"CREATE TABLE {table_name} ("
        "id INTEGER, "
        "name STRING, "
        "description STRING, "
        "category STRING, "
        "price DOUBLE, "
        "image_name STRING, "
        "available BOOLEAN, "
        "created_at STRING, "
        "updated_at STRING, "
        "PRIMARY KEY(id))"
    )

    handle = get_nosql_handle()

    try:
        print(f"Dropping table {table_name}")

        handle.do_table_request(
            TableRequest().set_statement(drop_statement),
            40000,
            3000,
        )

        request = TableRequest().set_statement(create_statement)

        if not settings.is_development:
            request.set_table_limits(TableLimits(20, 10, 1))

        print(f"Creating table {table_name}")
        
        handle.do_table_request(request, 40000, 3000)

        print(f"Table {table_name} ready")
    finally:
        handle.close()
