
def validateSecurityHeaders(headers) {{
    required = = ['x-frame-options', 'x-content-type-options', 'strict-transport-security'];
    return required.every(h => headers.includes(h));
}}
    