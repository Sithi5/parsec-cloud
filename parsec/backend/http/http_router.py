# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import re

mapping = [
    (rb"^/api/invite(.*)$", "http_invite_redirect"),
    (rb"^/api/test(.*)$", "http_test_redirect"),
]


class http_router:
    """Small router to handle http request"""

    def __init__(self):
        self._mapping = mapping

    @property
    def get_mapping(self):
        return self._mapping

    async def is_route(self, url: bytes):
        """Return the corresponding method_name if the url match a mapping route.

        if no route found, return None
        """
        match = None
        for regex, method_name in self._mapping:
            match = re.match(regex, url)
            if match:
                return method_name
        return None

    async def get_method_name(self, url: bytes):
        """ Same as is_route but get 404 method_name if no other route found"""
        method_name = await self.is_route(url)
        if not method_name:
            method_name = self.get_404_method_name()
        return method_name

    def get_404_method_name(self):
        """Return the 404 method_name"""
        return "http_404"

    async def get_regexs_from_method_name(self, test_method_name=None):
        """Return all mapping regexs matching with the method_name"""
        regexs = []
        for regex, method_name in self._mapping:
            if method_name == test_method_name:
                regexs.append(regex)
        return regexs
