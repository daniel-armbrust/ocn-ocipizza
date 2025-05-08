CREATE TABLE IF NOT EXISTS pizza (
    id INTEGER,
    name STRING,
    description STRING,
    image STRING,
    price NUMBER,
    json_replica JSON,
PRIMARY KEY(id))