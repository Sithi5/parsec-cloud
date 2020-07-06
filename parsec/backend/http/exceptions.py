# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS
"""
Define all the HTTPError classes
"""

# Base classes for all http errors


class HTTPError(Exception):
    """
    Base class for all fs exceptions
    """

    pass


class HTTPNoRouteFound(HTTPError):
    pass
