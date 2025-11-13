# Copyright 2024 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sentry SDK configuration and utility functions."""

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def get_event_level():
    """Get level of events to monitor (errors only, or error and warnings)."""
    if os.environ.get("SENTRY_CATCH_WARNINGS", False):
        return logging.WARNING
    return logging.ERROR


def before_send(event, hint):
    """
    Process events before sending to Sentry.
    Extracts request_data from RenderingError exceptions and adds it to context
    without affecting issue fingerprinting.
    """
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        # Check if the exception has request_data attribute (like RenderingError)
        if hasattr(exc_value, 'request_data') and exc_value.request_data:
            # Add the request data to contexts instead of the event itself
            # This prevents it from affecting issue grouping
            event.setdefault('contexts', {})
            event['contexts']['request_data'] = {
                'content_count': len(exc_value.request_data.get('content', [])),
                'report_clusters': list(exc_value.request_data.get('report_data', {}).get('reports', {}).keys()),
            }
            # Optionally store full payload in extra (less visible in Sentry UI)
            event.setdefault('extra', {})
            event['extra']['full_request_payload'] = str(exc_value.request_data)

        # If there's an original_exception, include it in extra
        if hasattr(exc_value, 'original_exception') and exc_value.original_exception:
            event.setdefault('extra', {})
            event['extra']['original_exception'] = str(exc_value.original_exception)

    return event


def init_sentry(dsn=None, transport=None, environment=None):
    """Configure and initialize sentry SDK for this project."""
    if dsn:
        logging.getLogger(__name__).info("Initializing sentry")
        sentry_logging = LoggingIntegration(level=logging.INFO, event_level=get_event_level())

        sentry_sdk.init(
            dsn=dsn,
            ca_certs="/etc/pki/tls/certs/ca-bundle.crt",
            integrations=[sentry_logging],
            max_breadcrumbs=15,
            transport=transport,
            environment=environment,
            before_send=before_send,
        )
