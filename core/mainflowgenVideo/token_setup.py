def build_token_setup(token_data, email_parse_data):
    """Build token setup với cookie string hoàn chỉnh.
    
    Args:
        token_data: Dict chứa sessionToken, csrfToken
        email_parse_data: Dict chứa email, EMAIL (encoded)
        
    Returns:
        dict: Token setup data
    """
    from core.constants.project_constants import (
        GA_DEFAULT, GA_CODE, GA_X2GNH8R5NS_VALUE,
        GA_SECONDARY, GA_X5V89YHGSH, GA_5K7X2T4V16, GA_4L3D49E8S8,
        CALLBACK_URL_WITH_PROJECT
    )
    
    # Google Analytics values
    ga = GA_DEFAULT
    ga_code = GA_CODE
    ga_x2gnh8r5ns = GA_X2GNH8R5NS_VALUE
    
    # Build full cookie string
    cookie_string = (
        f"_ga_X2GNH8R5NS=GS2.1.s1763545188$o40$g1$t1763546620$j46$l0$h1101075340; "
        f"_ga={GA_SECONDARY}; "
        f"_ga_X5V89YHGSH={GA_X5V89YHGSH}; "
        f"_ga_5K7X2T4V16={GA_5K7X2T4V16}; "
        f"_ga_4L3D49E8S8={GA_4L3D49E8S8}; "
        f"EMAIL={email_parse_data['EMAIL']}; "
        f"__Host-next-auth.csrf-token={token_data['csrfToken']}; "
        f"email={email_parse_data['email']}; "
        f"__Secure-next-auth.callback-url={CALLBACK_URL_WITH_PROJECT}; "
        f"__Secure-next-auth.session-token={token_data['sessionToken']};"
    )
    
    return {
        "sessionToken": token_data['sessionToken'],
        "Secure-next-auth.callback-url": "https%3A%2F%2Flabs.google%2Ffx",
        "Host-next-auth.csrf-token": token_data['csrfToken'],
        "ga": ga,
        "ga_code": ga_code,
        "_ga_X2GNH8R5NS": ga_x2gnh8r5ns,
        "cookie": cookie_string
    }
