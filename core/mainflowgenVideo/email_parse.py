def email_parse(raw_email):
    """Parse email thành các format khác nhau.
    
    Args:
        raw_email: Email gốc (ví dụ: long564288@tlultra12.io.vn)
    
    Returns:
        dict: {
            'email': URL-encoded email,
            'emailDefault': Email gốc,
            'EMAIL': URL-encoded email với dấu ngoặc kép
        }
    """
    from urllib.parse import quote
    
    # email (URL-encoded)
    email_encoded = quote(raw_email, safe='')
    
    # EMAIL (encode + thêm dấu ngoặc kép %22)
    email_with_quotes = f'%22{quote(raw_email, safe="")}%22'
    
    return {
        'email': email_encoded,           # long564288%40tlultra12.io.vn
        'emailDefault': raw_email,        # long564288@tlultra12.io.vn
        'EMAIL': email_with_quotes        # "%22long564288%40tlultra12.io.vn%22"
    }