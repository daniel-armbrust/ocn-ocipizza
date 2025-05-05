CREATE TABLE IF NOT EXISTS user (
    id INTEGER,
    name STRING,
    email STRING,
    password STRING,
    telephone STRING,
    verified BOOLEAN DEFAULT FALSE,
    json_replica JSON,           
PRIMARY KEY(id))