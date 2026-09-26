"""End-to-end test: Snowflake -> Gemini -> ElevenLabs.

1. Runs a query in Snowflake (key-pair auth, works headless on a droplet).
2. Sends the result to Gemini to turn into a short spoken sentence.
3. Sends that sentence to ElevenLabs and saves pipeline_output.mp3.

.env variables:
    SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER    required
    SNOWFLAKE_PRIVATE_KEY_PATH           optional, defaults to rsa_key.p8
    SNOWFLAKE_PRIVATE_KEY_PASSPHRASE     optional
    SNOWFLAKE_ROLE / _WAREHOUSE / _DATABASE / _SCHEMA  optional
    SNOWFLAKE_QUERY                      optional, overrides the default test query
    GEMINI_API_KEY, ELEVENLABS_API_KEY   required
    GEMINI_MODEL, ELEVENLABS_VOICE_ID    optional

Flags: --snowflake-only, --no-audio, --play
"""

import os
import sys
from pathlib import Path

import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env", encoding="utf-8-sig")

DEFAULT_QUERY = (
    "SELECT CURRENT_USER() AS user_name, CURRENT_ACCOUNT() AS account, "
    "CURRENT_REGION() AS region, CURRENT_VERSION() AS version"
)
DEFAULT_VOICE_ID = "Vs5CmVCVJwW4odQS2pVf"


def env(name, default=None):
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default


def require(*names):
    missing = [n for n in names if not env(n)]
    if missing:
        sys.exit(f"Missing in .env: {', '.join(missing)}")


def load_private_key():
    key_path = Path(env("SNOWFLAKE_PRIVATE_KEY_PATH", "rsa_key.p8"))
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


def query_snowflake():
    require("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER")
    params = {
        "account": env("SNOWFLAKE_ACCOUNT"),
        "user": env("SNOWFLAKE_USER"),
        "role": env("SNOWFLAKE_ROLE"),
        "warehouse": env("SNOWFLAKE_WAREHOUSE"),
        "database": env("SNOWFLAKE_DATABASE"),
        "schema": env("SNOWFLAKE_SCHEMA"),
    }
    params = {k: v for k, v in params.items() if v}
    if env("SNOWFLAKE_AUTH", "keypair").lower() == "browser":
        params["authenticator"] = "externalbrowser"
    else:
        params["private_key"] = load_private_key()

    sql = env("SNOWFLAKE_QUERY", DEFAULT_QUERY)
    print(f"[1/3] Snowflake: {params['account']} as {params['user']}")
    with snowflake.connector.connect(**params) as conn, conn.cursor() as cur:
        cur.execute(sql)
        columns = [c[0] for c in cur.description]
        rows = [dict(zip(columns, r)) for r in cur.fetchmany(20)]
    print(f"      {len(rows)} row(s): {rows}")
    return rows


def ask_gemini(rows):
    require("GEMINI_API_KEY")
    from google import genai

    model = env("GEMINI_MODEL", "gemini-3.8-flash")
    prompt = (
        "You are the voice of a robot car. In one or two short, friendly "
        "sentences suitable for text-to-speech (no markdown, no lists), "
        f"summarize this data from our database: {rows}"
    )
    print(f"[2/3] Gemini ({model})")
    client = genai.Client(api_key=env("GEMINI_API_KEY"))
    text = client.models.generate_content(model=model, contents=prompt).text.strip()
    print(f"      {text}")
    return text


def speak(text, play=False):
    require("ELEVENLABS_API_KEY")
    from elevenlabs.client import ElevenLabs

    print("[3/3] ElevenLabs")
    client = ElevenLabs(api_key=env("ELEVENLABS_API_KEY"))
    audio = b"".join(client.text_to_speech.convert(
        text=text,
        voice_id=env("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID),
        model_id="eleven_flash_v2_5",
        output_format="mp3_44100_128",
    ))
    out = HERE / "pipeline_output.mp3"
    out.write_bytes(audio)
    print(f"      saved {len(audio)} bytes to {out.name}")
    if play and sys.platform == "win32":
        os.startfile(out)


def main():
    args = set(sys.argv[1:])
    rows = query_snowflake()
    if "--snowflake-only" in args:
        return
    text = ask_gemini(rows)
    if "--no-audio" not in args:
        speak(text, play="--play" in args)
    print("Pipeline OK")


if __name__ == "__main__":
    main()
