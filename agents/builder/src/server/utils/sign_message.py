import json
import base58
from solders.keypair import Keypair


async def payload_signing(body: dict, private_key: bytes) -> str | None:
    message = json.dumps(body).encode("utf-8")

    keypair = Keypair.from_bytes(private_key)
    signed_message = keypair.sign(message)
    combined_payload = signed_message.signature + message
    return base58.b58encode(combined_payload).decode("utf-8")
