# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS
from urllib.parse import urlparse
from parsec._version import __version__ as parsec_version
from wsgiref.handlers import format_date_time
from parsec.core.types import BackendAddr
from parsec.backend.config import BackendConfig

import jinja2
import h11


def render_jinja_html(template_loc, file_name, **context):
    """Render html template with jinja"""
    # use package loader instead of filesystemloader
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_loc + "/"))
    jinja2_template = jinja2_env.get_template(file_name)
    jinja2_template_render = jinja2_template.render(context)
    return jinja2_template_render


def create_parsec_url(config: BackendConfig):
    """Return parsec url from backend_addr if exist, otherwise create one"""
    if not config.backend_addr:
        backend_addr = BackendAddr(hostname="localhost", port=6888)
    else:
        backend_addr = config.backend_addr

    return backend_addr.to_url()


def set_http_headers(data, headers=[]):
    """Return headers after adding date, server infos and Content-Length"""
    headers = list(headers)
    headers.append(("Date", format_date_time(None).encode("ascii")))
    headers.append(("Server", f"parsec/{parsec_version} {h11.PRODUCT_ID}"))
    headers.append(("Content-Length", str(len(data))))
    return headers


def http_redirect_to_parsec(url: bytes, config: BackendConfig, *arg, **kwarg):
    """Redirect the http invite request to a parsec url request"""
    location = create_parsec_url(config=config) + "/"
    parsed_url = urlparse(url)
    query_string = parsed_url.query.decode("utf-8")
    location = location + query_string
    headers = [("location", location)]
    data = b""
    return 302, set_http_headers(headers=headers, data=data), data


def http_404(*arg, **kwarg):
    """Return the 404 view"""
    status_code = 404
    # voir comment mettre
    template = render_jinja_html("parsec/backend/http/static", "404.html")
    data = template.encode("utf-8")
    return status_code, set_http_headers(data=data), data


# todo
# create_parsec_addr > config_backend_addr BackendAddr
