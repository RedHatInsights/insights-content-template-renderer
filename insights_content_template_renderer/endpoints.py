"""
Contains service endpoints.
"""

import logging
import os
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator

from insights_content_template_renderer.sentry import init_sentry
from insights_content_template_renderer.utils import render_reports, RenderingError
from insights_content_template_renderer.models import RendererRequest, RendererResponse


app = FastAPI()
log = logging.getLogger(__name__)

init_sentry(
    os.environ.get("SENTRY_DSN", None), None, os.environ.get("SENTRY_ENVIRONMENT", None)
)
instrumentator = Instrumentator().instrument(app)

@app.exception_handler(RenderingError)
async def rendering_error_handler(request, exc: RenderingError):
    """Handle RenderingError exceptions and return appropriate response."""
    return PlainTextResponse("Internal Server Error", status_code=500)

@app.on_event("startup")
async def expose_metrics():
    instrumentator.expose(app, endpoint='/metrics', tags=['metrics'])


@app.post("/rendered_reports", response_model=RendererResponse)
@app.post("/v1/rendered_reports", response_model=RendererResponse)
async def rendered_reports(data: RendererRequest):
    """
    Endpoint for rendering reports based on DoT.js content templates and report details.

    :param data: request containing JSON body with required data
    :return: JSON with rendered reports
    """
    log.info("Received request for /rendered_reports")
    log.debug("Rendering report")
    try:
        rendered_report = render_reports(data)
        log.debug("Report successfully rendered")
        return rendered_report

    except Exception as exc:
        # Wrap the exception with request data for debugging
        error = RenderingError(
            message=f"error rendering template: {exc}",
            original_exception=exc,
            request_data=data.model_dump()
        )
        log.error(str(error))
        # Re-raise so Sentry can capture it with the request_data
        raise error from exc
