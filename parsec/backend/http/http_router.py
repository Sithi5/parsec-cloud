# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import re
from parsec.backend.http.http_controller import http_invite_redirect, http_404

mapping = [
    (rb"^/api/invite(.*)$", http_invite_redirect),
    (rb"^/api/test(.*)$", http_invite_redirect),
]


class http_router:
    """Small router to handle http request"""

    def __init__(self):
        self._mapping = mapping

    @property
    def get_mapping(self):
        return self._mapping

    async def is_route(self, url: bytes):
        """Return the corresponding controller if the url match a mapping route.

        if no route found, return None
        """
        match = None
        for regex, controller in self._mapping:
            if match:
                break
            match = re.match(regex, url)
        if match:
            return controller
        return None

    async def get_controller(self, url: bytes):
        """ Same as is_route but raise an HTTPNoRouteFound error if no route found"""
        controller = await self.is_route(url)
        if not controller:
            controller = self.get_404_controller()
        return controller

    def get_404_controller(self):
        """Return the 404 controller"""
        return http_404

    async def get_regexs_from_controller(self, test_controller=None):
        """Return all mapping regexs matching with the controller"""
        regexs = []
        for regex, controller in self._mapping:
            if controller == test_controller:
                regexs.append(regex)
        return regexs
