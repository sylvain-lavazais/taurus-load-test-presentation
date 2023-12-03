from yoyo import step

steps = [
        step(
                """
                CREATE TABLE IF NOT EXISTS message
                (
                    "key"        text PRIMARY KEY,
                    "attributes" jsonb
                );
                """
        )
]
