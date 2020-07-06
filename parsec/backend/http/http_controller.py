# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS
# from urllib.parse import urlparse, parse_qs
# from parsec.core.types.backend_address import BackendInvitationAddr

import jinja2

# need to get addr from the backend directly
ADDR_TEST = "localhost"
PORT_TEST = 6888


def render_jinja_html(template_loc, file_name, **context):
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_loc + "/"))
    jinja2_template = jinja2_env.get_template(file_name)
    jinja2_template_render = jinja2_template.render(context)
    return jinja2_template_render


async def http_invite_redirect(url: bytes):
    print("INVITE REDIRECT")
    # parsed_url = urlparse(url)
    # query_string = parsed_url.query
    # parsed_query_string = parse_qs(query_string)
    try:
        # organization_id = parsed_query_string[b"organization_id"]
        # token = parsed_query_string[b"token"]
        # invitation_type = parsed_query_string[b"invitation_type"]
        # use_ssl = not parsed_query_string[b"no_ssl"]
        # # using BackendInvitationAddr to get an url maybe ?
        # addr = BackendInvitationAddr(
        #     organization_id=organization_id,
        #     invitation_type=invitation_type,
        #     token=token,
        #     hostname=ADDR_TEST,
        #     port=PORT_TEST,
        #     use_ssl=use_ssl,
        # )
        headers = [("location", "parsec://localhost/api")]
        data = b"licenseID=string&content=string&/paramsXML=string"
    except (Exception) as e:
        print("exception appened ", e)
        return 400, [], b""
    return 302, headers, data


async def http_test_redirect(url: bytes):
    print("TEST REDIRECT")
    return http_invite_redirect(url)


async def http_404():
    headers = []
    status_code = 404
    template = render_jinja_html("parsec/backend/http/static", "404.html")
    data = template.encode("utf-8")
    return status_code, headers, data
