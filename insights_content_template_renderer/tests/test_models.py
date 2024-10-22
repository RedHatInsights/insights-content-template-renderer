from insights_content_template_renderer.models import *
from insights_content_template_renderer.data import request_data_example


def test_renderer_request():
    req = RendererRequest.parse_obj(request_data_example)
    assert req.\
        report_data.\
        reports["5d5892d3-1f74-4ccf-91af-548dfc9767aa"].\
        reports[0].component == \
            "ccx_rules_ocp.external.rules.1.report"
