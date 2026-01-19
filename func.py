import io
import json
import requests
import oci
from fdk import response
from oci.signer import Signer

# ------------------------
# OCI Config - Load ONCE outside handler for performance
# ------------------------
CONFIG_PATH = "/function/oci_config/config"
config = oci.config.from_file(CONFIG_PATH)

# Initialize Signer
signer = Signer(
    tenancy=config["tenancy"],
    user=config["user"],
    fingerprint=config["fingerprint"],
    private_key_file_location=config["key_file"]
)

ODA_HOST = "https://oda-4a1c4d97c8b7416e90a8677ebeda76d4-da73696e.data.digitalassistant.oci.oraclecloud.com"

def handler(ctx, data: io.BytesIO = None):
    try:
        if data is None:
            raise ValueError("Request body is empty")

        req = json.loads(data.getvalue())

        botId = req.get("botId")
        entityId = req.get("entityId")
        pushRequestId = req.get("pushRequestId")

        if not all([botId, entityId, pushRequestId]):
            raise ValueError("botId, entityId, and pushRequestId are required")

        # Build payload
        payload = {k: req[k] for k in ("add", "modify", "delete") if k in req and req[k]}
        if not payload:
            raise ValueError("At least one of add, modify, or delete must be provided")

        # PATCH URL
        path = f"/api/v1/bots/{botId}/dynamicEntities/{entityId}/pushRequests/{pushRequestId}/values"
        url = f"{ODA_HOST}{path}"

        # ---------------------------------------------------------
        # THE FIX: Use 'auth=signer' instead of 'signers.sign_request'
        # ---------------------------------------------------------
        resp = requests.patch(
            url, 
            json=payload, 
            auth=signer,    # The signer automatically handles headers/signing
            timeout=30
        )

        return response.Response(
            ctx,
            response_data=resp.text,
            headers={"Content-Type": "application/json"},
            status_code=resp.status_code
        )

    except Exception as e:
        return response.Response(
            ctx,
            response_data=json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )