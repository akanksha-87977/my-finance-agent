"""Startup entrypoint for uvicorn.

The repo's package layout isn\'t always discovered correctly by uvicorn
in some execution environments. This module provides a stable import
target to expose `app`.
"""

"""See package notes in this file.

We intentionally import the app using relative import.
"""

from .main import app  # re-export

__all__ = ["app"]


