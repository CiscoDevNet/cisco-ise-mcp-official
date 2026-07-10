# Shared pytest fixtures

import os

# clients/settings.py instantiates the ISESettings singleton at import time,
# and ISE_IP / API_USERNAME / API_PWD are required fields. CI runners have no
# .env file, so importing any handler (via clients.client_factory) would raise
# a pydantic ValidationError before a single test runs. Seed dummy credentials
# here so the suite is hermetic and never depends on a local .env. Use
# setdefault so a developer's real exported credentials are never overridden.
os.environ.setdefault("ISE_IP", "127.0.0.1")
os.environ.setdefault("API_USERNAME", "test-user")
os.environ.setdefault("API_PWD", "test-password")
