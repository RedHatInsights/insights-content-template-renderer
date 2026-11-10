from typing import Any

from pydantic import BaseModel

from insights_content_template_renderer.data import (
    content_example,
    request_data_example,
    response_data_example,
)


class Content(BaseModel):
    plugin: dict
    error_keys: dict
    generic: str
    summary: str
    resolution: str
    more_info: str
    reason: str
    HasReason: bool

    class Config:
        schema_extra = {"example": content_example}


class Report(BaseModel):
    type: str
    component: str
    key: str
    details: dict

    class Config:
        schema_extra = {
            "example": {
                "type": "rule",
                "component": "rule.report",
                "key": "RULE",
                "details": {},
            }
        }


class ReportPerCluster(BaseModel):
    reports: list[Report]


class RenderedReport(BaseModel):
    rule_id: str
    error_key: str
    resolution: str
    reason: str
    description: str


class ReportData(BaseModel):
    clusters: list[str]
    reports: dict[str, ReportPerCluster]

    class Config:
        schema_extra = {
            "example": {
                "clusters": ["e1a379e4-9ac5-4353-8f82-ad066a734f18"],
                "reports": {
                    "e1a379e4-9ac5-4353-8f82-ad066a734f18": {
                        "reports": [
                            {
                                "type": "rule",
                                "component": "rule_1.report",
                                "key": "RULE_1",
                                "details": {},
                            },
                            {
                                "type": "rule",
                                "component": "rule_2.report",
                                "key": "RULE_2",
                                "details": {},
                            },
                        ]
                    }
                },
            }
        }


class RendererRequest(BaseModel):
    content: list[Content]
    report_data: ReportData

    class Config:
        schema_extra = {"example": request_data_example}


class RendererResponse(BaseModel):
    clusters: list[str]
    reports: dict[str, list[RenderedReport]]

    class Config:
        schema_extra = {"example": response_data_example}


class RenderItem(BaseModel):
    """A single recommendation whose template fields should be rendered."""

    template: dict[str, str]
    data: dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "template": {
                    "reason": "Test workload {{=pydata.name}} has a finding",
                    "resolution": "Apply the test resolution to {{=pydata.name}}",
                },
                "data": {"name": "my-app"},
            }
        }


class RenderItemsRequest(BaseModel):
    """Batch request for rendering DoT.js template fields."""

    items: list[RenderItem]

    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "template": {
                            "reason": "Test workload {{=pydata.name}} has a finding",
                            "resolution": "Apply the test resolution to {{=pydata.name}}",
                        },
                        "data": {"name": "my-app"},
                    }
                ]
            }
        }


class RenderedItem(BaseModel):
    """Result of rendering a single recommendation's template fields."""

    rendered: dict[str, str]
    errors: dict[str, str]

    class Config:
        schema_extra = {
            "example": {
                "rendered": {"reason": "Test workload my-app has a finding"},
                "errors": {"resolution": "Failed to execute DoT.js template"},
            }
        }


class RenderItemsResponse(BaseModel):
    """Batch response with rendered template fields."""

    items: list[RenderedItem]

    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "rendered": {"reason": "Test workload my-app has a finding"},
                        "errors": {"resolution": "Failed to execute DoT.js template"},
                    }
                ]
            }
        }
