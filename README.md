ODA Dynamic Entities Patch Function

This OCI Function provides a secure bridge to call the Oracle Digital Assistant (ODA) REST API. Specifically, it allows you to PATCH dynamic entity values using OCI Signature authentication.
💡 Why this function exists?

This function acts as a Custom Signing Proxy.

Currently, Oracle Integration Cloud (OIC) faces a limitation where the standard REST Adapter cannot correctly sign PATCH requests for ODA Dynamic Entities. The ODA API requires a specific OCI Signature (including the x-content-sha256 header) that the OIC REST Adapter does not generate for the PATCH verb.

This Python function solves that by:

    Receiving a standard JSON payload from OIC via a POST request.

    Using the official oci.signer library to properly sign the request.

    Executing the PATCH call to ODA and returning the result to OIC.

🚀 Features

    OIC Bridge: Allows OIC to effectively "PATCH" ODA entities via a simple POST call to this function.

    OCI Signer Integration: Uses oci.signer.Signer to handle complex RSA-SHA256 request signing.

    Resource Principal Ready: Built to work with OCI Functions execution environment.

📂 Project Structure
Plaintext

.
├── func.py                # Main Python logic and ODA API call
├── func.yaml              # Function configuration (timeout, memory)
├── requirements.txt       # Dependencies (oci, requests, fdk)
├── oci_config/
│   ├── config.example     # Template for OCI credentials
│   └── oci_key.pem        # (Ignored by Git) Your private API key
└── .gitignore             # Ensures secrets are never pushed to GitHub

🛠️ Setup Instructions
1. Authentication

To run this function, you must provide OCI API credentials.

    Copy oci_config/config.example to oci_config/config.

    Fill in your user, fingerprint, tenancy, and region.

    Place your OCI private key file at oci_config/oci_key.pem.

    Note: The key_file path in the config must be /function/oci_config/oci_key.pem to work inside the OCI Function container.

2. Deployment
Bash

# Deploy to your OCI application
fn deploy --app <your-app-name>

📡 Usage
Invoke from OIC

In your OIC Integration, use the OCI Functions Adapter or a standard REST Adapter to send a POST request to this function.

Sample Payload:
JSON

{
    "botId": "ocid1.odabot...",
    "entityId": "myDynamicEntity",
    "pushRequestId": "request-123",
    "add": [
        {
            "value": "New Item",
            "canonicalName": "NEW_ITEM"
        }
    ],
    "modify": [],
    "delete": []
}

⚠️ Important Security Note

The oci_config/ folder contains sensitive credentials. Never remove it from .gitignore.


To make your OCI Function easy to use within OIC (Oracle Integration Cloud), you need to know exactly what the request and response objects look like.

Since your function is essentially a "Proxy," it takes the ODA payload and returns the ODA response directly.
1. Sample Request Body (POST to Function)

This is what you will send from OIC to your OCI Function. The ODA API allows you to perform three types of operations in a single call.
JSON

{
  "botId": "ocid1.odabot.oc1.ap-singapore-1.aaaaaaaaxxx...",
  "entityId": "PizzaToppings",
  "pushRequestId": "req-998877",
  "add": [
    {
      "value": "Pineapple",
      "canonicalName": "PINEAPPLE",
      "synonyms": ["Ananas", "Hawaiian Style"]
    }
  ],
  "modify": [
    {
      "value": "Pepperoni",
      "canonicalName": "PEPPERONI_HOT",
      "synonyms": ["Spicy Salami"]
    }
  ],
  "delete": [
    {
      "value": "Mushrooms"
    }
  ]
}

2. Sample Success Response (From Function)

When the OCI Function successfully signs and forwards the request, ODA returns a 200 OK or 202 Accepted along with a summary of the processed items.
JSON

{
  "status": "success",
  "pushRequestId": "req-998877",
  "summary": {
    "addedCount": 1,
    "modifiedCount": 1,
    "deletedCount": 1
  },
  "details": "The dynamic entity values have been updated successfully."
}

3. Sample Error Response

If something goes wrong (e.g., the botId is incorrect or the OCI Signer fails), your try/except block will catch it and return a 500 error:
