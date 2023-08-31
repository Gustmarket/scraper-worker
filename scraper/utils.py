from urllib.parse import urlparse


def get_main_domain(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        parts = parsed_url.netloc.split('.')
        if len(parts) > 1:
            return '.'.join(parts[-2:])
        else:
            return parsed_url.netloc
    else:
        return None
