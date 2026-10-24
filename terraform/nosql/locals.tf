#
# nosql/locals.tf
#

locals {
  # Nome lógico utilizado pelo pizza-service para persistir as pizzas.
  table_name = "pizzas"

  # Nome lógico utilizado pelo delivery-service para persistir as áreas.
  delivery_areas_table_name = "delivery_areas"

  # Nome lógico utilizado pelo order-service para persistir os pedidos.
  orders_table_name = "orders"

  # O schema é congelado porque tabelas Global Active precisam permanecer
  # imutáveis depois que a réplica regional é criada.
  ddl_statement = <<-DDL
    CREATE TABLE IF NOT EXISTS pizzas (
      id STRING,
      name STRING,
      description STRING,
      category STRING,
      price NUMBER,
      image_name STRING,
      available BOOLEAN,
      created_at TIMESTAMP(3),
      updated_at TIMESTAMP(3),
      PRIMARY KEY(id)
    ) WITH SCHEMA FROZEN FORCE
  DDL

  # Schema das áreas atendidas pelo delivery-service.
  delivery_areas_ddl_statement = <<-DDL
    CREATE TABLE IF NOT EXISTS delivery_areas (
      id STRING,
      name STRING,
      zip_code_start STRING,
      zip_code_end STRING,
      delivery_fee NUMBER,
      estimated_minutes INTEGER,
      active BOOLEAN,
      created_at TIMESTAMP(3),
      updated_at TIMESTAMP(3),
      PRIMARY KEY (id)
    ) WITH SCHEMA FROZEN FORCE
  DDL

  # Schema dos pedidos, incluindo os registros aninhados de cliente,
  # endereço e itens da compra.
  orders_ddl_statement = <<-DDL
    CREATE TABLE IF NOT EXISTS orders (
      id STRING,
      user_id STRING,
      customer RECORD(
        name STRING,
        email STRING,
        whatsapp STRING
      ),
      delivery_address RECORD(
        zip_code STRING,
        street STRING,
        number STRING,
        complement STRING,
        neighborhood STRING,
        city STRING,
        state STRING
      ),
      items ARRAY(
        RECORD(
          pizza_id STRING,
          name STRING,
          quantity INTEGER,
          unit_price NUMBER,
          subtotal NUMBER
        )
      ),
      subtotal NUMBER,
      delivery_fee NUMBER,
      total NUMBER,
      status STRING,
      payment_status STRING,
      idempotency_key STRING,
      created_at TIMESTAMP(3),
      updated_at TIMESTAMP(3),
      PRIMARY KEY(id)
    ) WITH SCHEMA FROZEN FORCE
  DDL

  # Limites fixos da tabela principal e da réplica regional.
  table_limits = {
    read_units     = 5
    write_units    = 5
    storage_gb     = 1
    replica_region = "sa-vinhedo-1"
  }
}
