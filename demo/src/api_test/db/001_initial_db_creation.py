from yoyo import step

steps = [
        step(
                """
                CREATE SCHEMA IF NOT EXISTS "deposit";
                """
        ),
        step(
                """
                CREATE TABLE IF NOT EXISTS "deposit"."message"
                (
                    "key"        text PRIMARY KEY,
                    "attributes" jsonb
                );
                """
        )
]
