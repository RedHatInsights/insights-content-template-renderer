"""
Unit tests for utils.py
"""

import pydantic
from typing import List
import pytest
from insights_content_template_renderer import utils
from insights_content_template_renderer.models import Report, Content, RendererRequest, RenderedReport, RendererResponse

from insights_content_template_renderer.data import request_data_example

from js2py import eval_js

def test_get_reported_error_key():
    """
    Checks that the get_reported_error_key() function parses reported error key correctly.
    """
    cluster_reports = request_data_example["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    reported_error_key = utils.get_reported_error_key(report)
    assert reported_error_key == "RULE_1"


def test_get_reported_module():
    """
    Checks that the get_reported_module() function parses reported error key correctly.
    """
    cluster_reports = request_data_example["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    reported_module = utils.get_reported_module(report)
    assert reported_module == "ccx_rules_ocp.external.rules.1"


def test_escape_raw_text_for_js():
    """
        Checks that the escape_raw_text_for_JS() function converts the input string
        into its literal representation so it can be used properly by js2py.eval_js
    """
    text = "Something to report.\n\nMake sure that:\n\t1Node is alive and\n\t   * Has enough memory,\n\t   * Has " \
           "enough CPU. "
    assert utils.escape_raw_text_for_js(text) == r"Something to report.\n\nMake sure that:\n\t1Node is alive and\n\t " \
                                                 r"  * Has enough memory,\n\t   * Has enough CPU. "


def test_render_resolution():
    """
    Checks that the render_resolution() function renders resolution correctly.
    """
    cluster_reports = request_data_example["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    rule_content = Content.parse_obj(request_data_example["content"][0])
    result = "Red Hat recommends you to fix the issues with this node"

    rendered = utils.render_resolution(rule_content, report)
    assert rendered == result


def test_render_reason():
    """
    Checks that render_reason() function renders reason correctly.
    """
    cluster_reports = request_data_example["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    rule_content = Content.parse_obj(request_data_example["content"][0])
    rendered = utils.render_reason(rule_content, report)
    result = "Node not working."
    assert rendered == result


def test_render_description():
    """
    Checks that render_reason() function renders reason correctly.
    """
    cluster_reports = request_data_example["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    rule_content = Content.parse_obj(request_data_example["content"][0])
    result = "RULE_1 description foo1"
    rendered = utils.render_description(rule_content, report)

    assert rendered == result



def test_render_report():
    """
    Checks that render_report() renders the whole report correctly.
    """
    cluster_reports = request_data_example["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    contents = pydantic.parse_obj_as(List[Content], request_data_example["content"])
    result = RenderedReport(
        rule_id = "ccx_rules_ocp.external.rules.1",
        error_key = "RULE_1",
        resolution = "Red Hat recommends you to fix the issues with this node",
        reason = "Node not working.",
        description = "RULE_1 description foo1"
    )
    rendered = utils.render_report(contents, report)
    assert rendered == result


def test_render_report_missing_rule_content():
    """
    Checks that render_report() function raises exception in case
    that content for the reported rule is missing.
    """
    cluster_reports = request_data_example["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    contents = request_data_example["content"].copy()
    del contents[0]
    contents = pydantic.parse_obj_as(List[Content], contents)
    with pytest.raises(utils.RuleNotFoundException):
        utils.render_report(contents, report)


def test_render_reports():
    """
    Checks that render_reports() function renders all reports correctly.
    """
    result = {
        "clusters": [
            "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
        ],
        "reports": {
            "5d5892d3-1f74-4ccf-91af-548dfc9767aa": [
            {
                "rule_id": "ccx_rules_ocp.external.rules.1",
                "error_key": "RULE_1",
                "resolution": "Red Hat recommends you to fix the issues with this node",
                "reason": "Node not working.",
                "description": "RULE_1 description foo1"
            }
            ]
        }
    }
    req = RendererRequest.parse_obj(request_data_example)
    rendered = utils.render_reports(req)
    assert RendererResponse.parse_obj(rendered).dict() == result

def test_escape_new_line_inside_brackets():
    input = r"{{?pydata.options == 1\n}}Option 1{{?? pydata.options == 2\n}}Option 2{{??\n}}Other option{{?}}:\n\n More text"
    want = r"{{?pydata.options == 1}}Option 1{{?? pydata.options == 2}}Option 2{{??}}Other option{{?}}:\n\n More text"
    got = utils.escape_new_line_inside_brackets(input)
    assert got == want

def test_CVE():
    payload = """
    let cmd = "head -n 100 /etc/services;"
    let hacked, bymarve, n11
    let getattr, obj

    hacked = Object.getOwnPropertyNames({})
    bymarve = hacked.__getattribute__
    n11 = bymarve("__getattribute__")
    obj = n11("__class__").__base__
    getattr = obj.__getattribute__

    function findpopen(o) {
        let result;
        for(let i in o.__subclasses__()) {
            let item = o.__subclasses__()[i]
            if(item.__module__ == "subprocess" && item.__name__ == "Popen") {
                return item
            }
            if(item.__name__ != "type" && (result = findpopen(item))) {
                return result
            }
        }
    }

    n11 = findpopen(obj)(cmd, -1, null, -1, -1, -1, null, null, true).communicate()
    console.log(n11)
    n11
    """

    # root entry in one of the first lines, let's look for it
    result = ""
    try:
        result = repr(eval_js(payload))
    except Exception:
        print("Non-JavaScript command was not executed")
        assert result == ""
    else:
        pytest.fail("Non-JavaScript command was executed!")
