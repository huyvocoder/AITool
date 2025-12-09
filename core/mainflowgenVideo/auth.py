def build_headers(token_data):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-csrf-token": token_data["csrfToken"],
        "authorization": f"Bearer {token_data['sessionToken']}",
        "user-agent": "Mozilla/5.0"
    }
    return headers