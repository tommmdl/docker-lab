from database import connect

with connect() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
print("Schema ready", flush=True)
