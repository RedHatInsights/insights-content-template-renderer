"""
Contains service endpoints.
"""

import logging
import os

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator

from insights_content_template_renderer.js_executor import shutdown_js_executor
from insights_content_template_renderer.models import (
    RendererRequest,
    RendererResponse,
    RenderItemsRequest,
    RenderItemsResponse,
)
from insights_content_template_renderer.sentry import init_sentry
from insights_content_template_renderer.utils import (
    RenderingError,
    render_items,
    render_reports,
)

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
    instrumentator.expose(app, endpoint="/metrics", tags=["metrics"])


@app.on_event("shutdown")
async def shutdown_workers():
    """Gracefully shutdown the JavaScript worker pool on application shutdown."""
    log.info("Application shutdown initiated, cleaning up worker pool")
    shutdown_js_executor()


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
        error = RenderingError(f"error rendering template: {exc}")
        log.exception(error)
        # Re-raise so Sentry can capture it with the request_data
        raise error from exc


@app.post("/v2/rendered_reports", response_model=RenderItemsResponse)
async def rendered_reports_v2(data: RenderItemsRequest) -> RenderItemsResponse:
    """
    Endpoint for batch rendering of DoT.js template fields.

    Each item contains a map of template fields and the data (pydata) to
    render them with. Fields that fail to render are reported in the item's
    errors map; the response preserves the request's item order.

    :param data: request containing JSON body with required data
    :return: JSON with rendered items
    """
    log.info("Received request for /v2/rendered_reports")
    log.debug("Rendering items")
    return render_items(data)
