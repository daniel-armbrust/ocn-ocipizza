import hashlib
import pathlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import pymysql

from config.settings import settings


CURRENT_DIR = pathlib.Path(__file__).resolve().parent
SCHEMA_FILE = CURRENT_DIR / "seed-users.sql"


DEMO_USERS = [
    {
        "id": uuid.UUID("11111111-1111-4111-8111-111111111111"),
        "full_name": "Maria Oliveira",
        "email": "maria.oliveira@example.com",
        "confirmed": True,
        "whatsapp": "+5511999999999",
        "password": "DemoPassword123!"
    },
    {
        "id": uuid.UUID("22222222-2222-4222-8222-222222222222"),
        "full_name": "Joao Silva",
        "email": "joao.silva@example.com",
        "confirmed": False,
        "whatsapp": "+5511988888888",
        "password": "DemoPassword123!"
    },
    {
        "id": uuid.UUID("33333333-3333-4333-8333-333333333333"),
        "full_name": "Rita de Cássia",
        "email": "rita.cassia@example.com",
        "confirmed": True,
        "whatsapp": "+5511977777777",
        "password": "DemoPassword123!"
    }
]


def _quote_identifier(value):
    return f"`{value.replace('`', '``')}`"


def _password_hash(password):
    salt = secrets.token_hex(16)
    iterations = 600000
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations
    ).hex()

    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def _token_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _execute_sql_file(cursor):
    statements = [
        statement.strip()
        for statement in SCHEMA_FILE.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]

    for statement in statements:
        cursor.execute(statement)


def _create_database_and_user(cursor):
    database = _quote_identifier(settings.mysql_database)
    user = settings.mysql_user.replace("'", "''")
    password = settings.mysql_password.replace("'", "''")

    cursor.execute(f"DROP DATABASE IF EXISTS {database}")
    cursor.execute(
        f"CREATE DATABASE {database} "
        "CHARACTER SET utf8mb4 "
        "COLLATE utf8mb4_0900_ai_ci"
    )
    cursor.execute(f"CREATE USER IF NOT EXISTS '{user}'@'%' IDENTIFIED BY '{password}'")
    cursor.execute(f"ALTER USER '{user}'@'%' IDENTIFIED BY '{password}'")
    cursor.execute(f"GRANT ALL PRIVILEGES ON {database}.* TO '{user}'@'%'")
    cursor.execute("FLUSH PRIVILEGES")
    cursor.execute(f"USE {database}")


def _insert_demo_users(cursor):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expires_at = now + timedelta(hours=24)

    for user in DEMO_USERS:
        cursor.execute(
            """
            INSERT INTO users (
                id,
                full_name,
                email,
                confirmed,
                whatsapp,
                password_hash,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user["id"].bytes,
                user["full_name"],
                user["email"],
                user["confirmed"],
                user["whatsapp"],
                _password_hash(user["password"]),
                now,
                now
            )
        )

        if not user["confirmed"]:
            confirmation_token = f"dev-confirm-{user['id']}"

            cursor.execute(
                """
                INSERT INTO email_confirmation_tokens (
                    id,
                    user_id,
                    token_hash,
                    created_at,
                    expires_at
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    uuid.uuid4().bytes,
                    user["id"].bytes,
                    _token_hash(confirmation_token),
                    now,
                    expires_at
                )
            )


def seed_users():
    print("Seeding users")

    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_root_user,
        password=settings.mysql_root_password,
        autocommit=False
    )

    try:
        with connection.cursor() as cursor:
            _create_database_and_user(cursor)
            _execute_sql_file(cursor)
            _insert_demo_users(cursor)

        connection.commit()
        print("Users seed completed")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
