"""Snowflake connection test.

Default auth is key-pair (works headless, e.g. on a DigitalOcean droplet).
Set SNOWFLAKE_AUTH=browser to use Google SSO via a local browser instead.

Expected .env variables:
    SNOWFLAKE_ACCOUNT              e.g. ORGNAME-ACCOUNTNAME
    SNOWFLAKE_USER                 Snowflake login name (see DESC USER / SELECT CURRENT_USER())
    SNOWFLAKE_PRIVATE_KEY_PATH     optional, defaults to rsa_key.p8 next to this file
    SNOWFLAKE_PRIVATE_KEY_PASSPHRASE  optional, only if the .p8 is encrypted
    SNOWFLAKE_ROLE / SNOWFLAKE_WAREHOUSE / SNOWFLAKE_DATABASE / SNOWFLAKE_SCHEMA  optional
"""

import os
import sys
from pathlib import Path

import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")


def env(name):
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


def load_private_key():
    key_path = Path(env("SNOWFLAKE_PRIVATE_KEY_PATH") or HERE / "rsa_key.p8")
    if not key_path.is_absolute():
        key_path = HERE / key_path
    passphrase = env("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
    key = serialization.load_pem_private_key(
        key_path.read_bytes(),
        password=passphrase.encode() if passphrase else None,
    )
    return key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def main():
    missing = [n for n in ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER") if not env(n)]
    if missing:
        sys.exit(f"Missing in .env: {', '.join(missing)}")

    params = {
        "account": env("SNOWFLAKE_ACCOUNT"),
        "user": env("SNOWFLAKE_USER"),
        "role": env("SNOWFLAKE_ROLE"),
        "warehouse": env("SNOWFLAKE_WAREHOUSE"),
        "database": env("SNOWFLAKE_DATABASE"),
        "schema": env("SNOWFLAKE_SCHEMA"),
    }
    params = {k: v for k, v in params.items() if v}

    if (env("SNOWFLAKE_AUTH") or "keypair").lower() == "browser":
        params["authenticator"] = "externalbrowser"
    else:
        params["private_key"] = load_private_key()

    print(f"Connecting to {params['account']} as {params['user']} "
          f"({params.get('authenticator', 'key-pair')})...")
    with snowflake.connector.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), "
                "CURRENT_DATABASE(), CURRENT_VERSION()"
            )
            user, role, wh, db, version = cur.fetchone()
    print("Connected successfully")
    print(f"  user={user} role={role} warehouse={wh} database={db} version={version}")


if __name__ == "__main__":
    main()
