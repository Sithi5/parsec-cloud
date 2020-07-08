# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import re
from parsec.backend.http.http_controller import http_404, http_invite_redirect


# callback sur fonction
mapping = [(rb"^/api/invite(.*)$", http_invite_redirect)]


def http_is_route(url: bytes):
    """Return the corresponding method if the url match a mapping route.
    if no route found, return None
    """
    match = None
    for regex, method in mapping:
        match = re.match(regex, url)
        if match:
            return method
    return None


def http_get_method(url: bytes):
    """ Same as is_route but get 404 method if no other route found"""
    method = http_is_route(url)
    if not method:
        method = http_get_404_method()
    return method


def http_get_404_method():
    """Return the 404 method"""
    return http_404


def http_get_regexs_from_method(test_method=None):
    """Return all mapping regexs matching with the method"""
    regexs = []
    for regex, method in mapping:
        if method == test_method:
            regexs.append(regex)
    return regexs
