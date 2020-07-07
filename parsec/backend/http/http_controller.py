# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS
from urllib.parse import urlparse, parse_qs
from parsec._version import __version__ as parsec_version
from wsgiref.handlers import format_date_time

from parsec.backend.http import http_router

import jinja2
import h11


class http_controller:
    """Small controller to handle http request"""

    def __init__(self, backend_addr, backend_port, router=http_router()):
        self._backend_addr = backend_addr
        self._backend_port = backend_port
        self._router = router

    async def __call__(self, url: bytes):
        """Call the controller with url to execute corresponding method if it match a route"""
        method_name = await self._router.get_method_name(url)
        method = getattr(self, method_name)
        status_code, headers, data = await method(url)
        return status_code, headers, data

    async def _render_jinja_html(self, template_loc, file_name, **context):
        """Render html template with jinja"""
        jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_loc + "/"))
        jinja2_template = jinja2_env.get_template(file_name)
        jinja2_template_render = jinja2_template.render(context)
        return jinja2_template_render

    async def create_parsec_url(self):
        """Return parsec url with the backend_addr and backend_port"""
        return "parsec://" + str(self._backend_addr) + ":" + str(self._backend_port) + "/"

    async def create_data_query_string(self, data: str = "", *args, **kwargs):
        """Add kwargs to query string"""
        for key, value in kwargs.items():
            if len(data) > 0:
                data = data + "&"
            data = data + str(key) + "=" + str(value)
        return data.encode("utf-8")

    async def _set_http_headers(self, headers, data):
        """Return headers after adding date, server infos and Content-Length"""
        headers.append(("Date", format_date_time(None).encode("ascii")))
        headers.append(("Server", f"parsec/{parsec_version} {h11.PRODUCT_ID}"))
        headers.append(("Content-Length", str(len(data))))
        return headers

    async def http_invite_redirect(self, url: bytes):
        """Redirect the http invite request to a parsec url request"""
        print("INVITE REDIRECT")
        parsed_url = urlparse(url)
        query_string = parsed_url.query
        parsed_query_string = parse_qs(query_string)
        try:
            organization_id = parsed_query_string[b"organization_id"]
            token = parsed_query_string[b"token"]
            invitation_type = parsed_query_string[b"invitation_type"]
            no_ssl = parsed_query_string[b"no_ssl"]
            location = await self.create_parsec_url()
            data = await self.create_data_query_string(
                organization_id=organization_id,
                token=token,
                invitation_type=invitation_type,
                no_ssl=no_ssl,
            )
            location = await self.create_parsec_url()
            data = await self.create_data_query_string(
                organization_id=organization_id,
                token=token,
                invitation_type=invitation_type,
                no_ssl=no_ssl,
            )
            headers = [("location", location)]
            headers = await self._set_http_headers(headers, data)
        except (Exception):
            return await self.http_404(url)
        return 302, headers, data

    async def http_test_redirect(self, url: bytes):
        """Simple test for the router"""
        print("TEST REDIRECT")
        return await self.http_invite_redirect(url)

    async def http_404(self, *arg, **kwarg):
        """Return the 404 view"""
        status_code = 404
        headers = []
        template = await self._render_jinja_html("parsec/backend/http/static", "404.html")
        data = template.encode("utf-8")
        headers = await self._set_http_headers(headers, data)
        return status_code, headers, data
