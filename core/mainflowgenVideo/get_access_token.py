def get_access_token(token_data, email_parse_data, log):
    """Lấy access token từ Google Labs API.
    
    Args:
        token_data: Dict chứa sessionToken, csrfToken
        email_parse_data: Dict chứa email, EMAIL (encoded)
        log: Widget tkinter để hiển thị log
        
    Returns:
        str: Access token
    """
    import requests
    from core.constants.project_constants import (
        AUTH_SESSION_URL, API_TIMEOUT, USER_AGENT,
        GA_DEFAULT, GA_CODE, GA_X2GNH8R5NS_VALUE,
        GA_X5V89YHGSH_SECONDARY, GA_X2GNH8R5NS_SECONDARY,
        CALLBACK_URL_ENCODED
    )
    
    log.insert("end", "🔹 Đang lấy access token từ Google Labs...\n")
    
    # Tạo cookie string theo format của n8n
    ga = GA_DEFAULT
    ga_code = GA_CODE
    ga_value = GA_X2GNH8R5NS_VALUE
    
    cookie_string = (
        f"_ga={ga}; "
        f"{ga_code}={ga_value}; "
        f"__Host-next-auth.csrf-token={token_data['csrfToken']}; "
        f"__Secure-next-auth.callback-url={CALLBACK_URL_ENCODED}; "
        f"email={email_parse_data['email']}; "
        f"EMAIL={email_parse_data['EMAIL']}; "
        f"_ga_X5V89YHGSH={GA_X5V89YHGSH_SECONDARY}; "
        f"_ga_X2GNH8R5NS={GA_X2GNH8R5NS_SECONDARY}; "
        f"__Secure-next-auth.session-token={token_data['sessionToken']}"
    )
    
    headers = {
        "cookie": cookie_string,
        "user-agent": USER_AGENT
    }
    
    try:
        response = requests.get(AUTH_SESSION_URL, headers=headers, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token', '')
            
            if access_token:
                log.insert("end", f"✅ Access token: {access_token[:30]}...\n")
                return access_token
            else:
                log.insert("end", "⚠️ Không tìm thấy access_token trong response\n")
                return None
        else:
            log.insert("end", f"❌ Lỗi HTTP {response.status_code}: {response.text[:100]}\n")
            return None
            
    except Exception as e:
        log.insert("end", f"❌ Lỗi khi lấy access token: {str(e)}\n")
        return None
