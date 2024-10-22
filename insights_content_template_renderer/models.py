from typing import List, Dict

from pydantic import BaseModel

from insights_content_template_renderer.data import \
        request_data_example, response_data_example, content_example


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
        schema_extra = {
            "example": content_example 
        }


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
                "details": {}
            }
        }

class ReportPerCluster(BaseModel):
    reports: List[Report]

class RenderedReport(BaseModel):
	rule_id: str
	error_key: str
	resolution: str
	reason: str
	description: str

class ReportData(BaseModel):
    clusters: List[str]
    reports: Dict[str, ReportPerCluster]

    class Config:
        schema_extra = {
            "example": {
                "clusters": [
                        "e1a379e4-9ac5-4353-8f82-ad066a734f18"
                ],
                "reports": {
                        "e1a379e4-9ac5-4353-8f82-ad066a734f18": {
                                "reports": [
                                        {
                                                "type": "rule",
                                                "component": "rule_1.report",
                                                "key": "RULE_1",
                                                "details": {}
                                        },
                                        {
                                                "type": "rule",
                                                "component": "rule_2.report",
                                                "key": "RULE_2",
                                                "details": {}
                                        }
                                ]
                        }
                }
            }
        }

class RendererRequest(BaseModel):
    content: List[Content]
    report_data: ReportData

    class Config:
        schema_extra = {
            "example": request_data_example
        }

class RendererResponse(BaseModel):
    clusters: List[str]
    reports: Dict[str, List[RenderedReport] ]

    class Config:
        schema_extra = {
            "example": response_data_example
        }
