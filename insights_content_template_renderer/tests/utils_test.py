"""
Unit tests for utils.py
"""

import json
from pathlib import Path
import pytest
from insights_content_template_renderer import utils
from copy import deepcopy

test_data = {}
test_data_path = Path(__file__).with_name("request_data_example.json")
with test_data_path.open(encoding="UTF-8") as f:
    test_data = json.load(f)


def test_get_reported_error_key():
    """
    Checks that the get_reported_error_key() function parses reported error key correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    reported_error_key = utils.get_reported_error_key(report)
    assert reported_error_key == "NODES_MINIMUM_REQUIREMENTS_NOT_MET"


def test_get_reported_module():
    """
    Checks that the get_reported_module() function parses reported error key correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    reported_module = utils.get_reported_module(report)
    assert reported_module == "ccx_rules_ocp.external.rules.nodes_requirements_check"


def test_get_reported_module_component_field_missing():
    """
    Checks that the get_reported_module() function raises error
    in case the required field is missing.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    del report["component"]
    with pytest.raises(ValueError):
        utils.get_reported_module(report)


def test_get_reported_error_key_key_field_missing():
    """
    Checks that the get_reported_error_key() function raises error
    in case the required field is missing.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    del report["key"]
    with pytest.raises(ValueError):
        utils.get_reported_error_key(report)


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
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    rule_content = test_data["content"][3].copy()
    result = "Red Hat recommends that you configure your nodes to meet the minimum resource requirements.\n\nMake " \
             "sure that:\n\n\n1. Node foo1 (undefined)\n   * Has enough memory, minimum requirement is 16. Currently " \
             "its only configured with 8.16GB.\n"

    rendered = utils.render_resolution(rule_content, report)
    assert rendered == result


def test_render_reason():
    """
    Checks that render_reason() function renders reason correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    rule_content = test_data["content"][3]
    rendered = utils.render_reason(rule_content, report)
    result = "Node not meeting the minimum " \
             "requirements:\n\n1. foo1\n  * Roles: undefined\n  * " \
             "Minimum memory requirement is 16, but the node is configured with 8.16.\n"
    assert rendered == result


def test_render_description():
    """
    Checks that render_reason() function renders reason correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    rule_content = test_data["content"][3]
    result = "An OCP node foo1 behaves unexpectedly when it doesn't meet the minimum resource requirements"
    rendered = utils.render_description(rule_content, report)

    assert rendered == result



def test_render_report():
    """
    Checks that render_report() renders the whole report correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    content = test_data["content"].copy()
    result = {
        "rule_id": "ccx_rules_ocp.external.rules.nodes_requirements_check",
        "error_key": "NODES_MINIMUM_REQUIREMENTS_NOT_MET",
        "resolution": "Red Hat recommends that you configure your nodes to meet the minimum "\
                      "resource requirements.\n\nMake sure that:\n\n\n1. Node foo1 (undefined)\n   * Has enough "\
                      "memory, minimum requirement is 16. Currently its only configured with 8.16GB.\n",
        "reason": "Node not meeting the minimum requirements:\n\n1. foo1\n  * Roles: undefined\n  * Minimum "\
                  "memory requirement is 16, but the node is configured with 8.16.\n",
        "description": "An OCP node foo1 behaves unexpectedly when it doesn't meet the minimum resource requirements",
    }
    rendered = utils.render_report(content, report)
    assert rendered == result


def test_render_report_missing_rule_content():
    """
    Checks that render_report() function raises exception in case
    that content for the reported rule is missing.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    content = test_data["content"].copy()
    del content[3]
    with pytest.raises(utils.RuleNotFoundException):
        utils.render_report(content, report)


def test_render_reports_v1():
    """
    Checks that render_reports() function renders all reports correctly.
    """
    data = deepcopy(test_data)
    result = {
        'clusters': [
            '5d5892d3-1f74-4ccf-91af-548dfc9767aa'
        ],
        'reports': {
            '5d5892d3-1f74-4ccf-91af-548dfc9767aa': [
                {
                    'rule_id': 'ccx_rules_ocp.external.rules.nodes_requirements_check',
                    'error_key': 'NODES_MINIMUM_REQUIREMENTS_NOT_MET',
                    'resolution': "Red Hat recommends that you configure your nodes to meet the minimum resource requirements.\n\nMake sure that:\n\n\n1. Node foo1 (undefined)\n   * Has enough memory, minimum requirement is 16. Currently its only configured with 8.16GB.\n",
                    'reason': "Node not meeting the minimum requirements:\n\n1. foo1\n  * Roles: undefined\n  * Minimum memory requirement is 16, but the node is configured with 8.16.\n",
                    'description': "An OCP node foo1 behaves unexpectedly when it doesn't meet the minimum resource requirements"
                },
                {
                    'rule_id': 'ccx_rules_ocp.external.rules.samples_op_failed_image_import_check',
                    'error_key': 'SAMPLES_FAILED_IMAGE_IMPORT_ERR',
                    'resolution': "Red Hat recommends that you to follow these steps:\n\n1. Fix 1, Try running:\n~~~\n# oc import-image <for the ImageStream(s) in question>\n~~~\n\n1. Fix 2, Try running:\n~~~\n# oc delete configs.samples cluster\n~~~",
                    'reason': "Due to a temporary hiccup talking to the Red Hat registry the openshift-samples failed to import some of the imagestreams.\n\n\nSource of the issue:\n\n**Cluster-operator:**  **openshift-samples**\n- *Condition:* Degraded\n- *Reason:* FailedImageImports\n- *Message:* Samples installed at 4.2.0, with image import failures for these imagestreams: php \n- *Last* Transition: 2020-03-19T08:32:53Z\n",
                    'description': "Pods could fail to start if openshift-samples is degraded due to FailedImageImport which is caused by a hiccup while talking to the Red Hat registry"
                },
                {
                    'rule_id': 'ccx_rules_ocp.external.rules.namespaces_with_overlapping_uid_ranges',
                    'error_key': 'NAMESPACES_WITH_OVERLAPPING_UID_RANGES',
                    'resolution': 'Red Hat recommends that you resolve the issue by following the steps in the [Knowledgebase Article](https://access.redhat.com/articles/6844071).',
                    'description': 'Namespaces with collision UID ranges do not meet the compliance requirements with many industry standards',
                    'reason': 'The following namespaces are detected to have collision UID ranges. Namespaces with collision UID ranges do not meet the compliance requirements with many industry standards. In some serious situations, it could lead to data exposure.\n\n\n- Namespaces: \n**openshift**, \n**test-1**, \n**test-2**, \n\n- Namespaces: \n**openshift-ingress-canary**, \n**test-3**, \n\n- Namespaces: \n**test-4**, \n**test-5**, \n**test-6**, \n'
                },
                {
                    'rule_id': 'ccx_rules_ocp.external.rules.cluster_wide_proxy_auth_check',
                    'error_key': 'AUTH_OPERATOR_PROXY_ERROR',
                    'resolution': "Red Hat recommends that you to follow steps in the KCS article.\n * [Authentication operator Degraded with Reason `WellKnownEndpointDegradedError`](https://access.redhat.com/solutions/4569191)\n",
                    'reason': "Requests to routes and/or the public API endpoint are not being proxied to the cluster.\n",
                    'description': "The authentication operator is degraded when cluster is configured to use a cluster-wide proxy"
                }
            ]
        }
    }
    rendered = utils.render_reports_v1(data)
    assert rendered == result


def test_render_reports_v1_missing_content():
    """
    Checks that render_reports() function raises exception if the content data are missing.
    """
    data = deepcopy(test_data)
    del data["content"]
    with pytest.raises(ValueError):
        utils.render_reports_v1(data)


def test_render_reports_v1_missing_report_data():
    """
    Checks that render_reports() function raises exception if the report data are missing.
    """
    data = deepcopy(test_data)
    del data["report_data"]
    with pytest.raises(ValueError):
        utils.render_reports_v1(data)


def test_render_reports_v1_missing_clusters():
    """
    Checks that render_reports() function raises exception
    if the data for reported clusters are missing.
    """
    data = deepcopy(test_data)
    del data["report_data"]["clusters"]
    with pytest.raises(ValueError):
        utils.render_reports_v1(data)


def test_render_reports_v1_missing_reports():
    """
    Checks that render_reports() function raises exception
    if the data for individual reports are missing.
    """
    data = deepcopy(test_data)
    print(test_data["report_data"])
    del data["report_data"]["reports"]
    with pytest.raises(ValueError):
        utils.render_reports_v1(data)
    print(test_data["report_data"])



def test_render_reports_v2():
    """
    Checks that render_reports() function renders all reports correctly.
    """
    data = deepcopy(test_data)
    result = {
        'clusters': [
            '5d5892d3-1f74-4ccf-91af-548dfc9767aa'
        ],
        'reports': {
            '5d5892d3-1f74-4ccf-91af-548dfc9767aa': {
                'nodes_requirements_check|NODES_MINIMUM_REQUIREMENTS_NOT_MET': {
                    'rule_id': 'ccx_rules_ocp.external.rules.nodes_requirements_check',
                    'error_key': 'NODES_MINIMUM_REQUIREMENTS_NOT_MET',
                    'resolution': "Red Hat recommends that you configure your nodes to meet the minimum resource requirements.\n\nMake sure that:\n\n\n1. Node foo1 (undefined)\n   * Has enough memory, minimum requirement is 16. Currently its only configured with 8.16GB.\n",
                    'reason': "Node not meeting the minimum requirements:\n\n1. foo1\n  * Roles: undefined\n  * Minimum memory requirement is 16, but the node is configured with 8.16.\n",
                    'description': "An OCP node foo1 behaves unexpectedly when it doesn't meet the minimum resource requirements"
                },
                'samples_op_failed_image_import_check|SAMPLES_FAILED_IMAGE_IMPORT_ERR': {
                    'rule_id': 'ccx_rules_ocp.external.rules.nodes_requirements_check',
                    'error_key': 'NODES_MINIMUM_REQUIREMENTS_NOT_MET',
                    'resolution': "Red Hat recommends that you configure your nodes to meet the minimum resource requirements.\n\nMake sure that:\n\n\n1. Node foo1 (undefined)\n   * Has enough memory, minimum requirement is 16. Currently its only configured with 8.16GB.\n",
                    'reason': "Node not meeting the minimum requirements:\n\n1. foo1\n  * Roles: undefined\n  * Minimum memory requirement is 16, but the node is configured with 8.16.\n",
                    'description': "An OCP node foo1 behaves unexpectedly when it doesn't meet the minimum resource requirements"
                },
                'samples_op_failed_image_import_check|SAMPLES_FAILED_IMAGE_IMPORT_ERR': {
                    'rule_id': 'ccx_rules_ocp.external.rules.samples_op_failed_image_import_check',
                    'error_key': 'SAMPLES_FAILED_IMAGE_IMPORT_ERR',
                    'resolution': "Red Hat recommends that you to follow these steps:\n\n1. Fix 1, Try running:\n~~~\n# oc import-image <for the ImageStream(s) in question>\n~~~\n\n1. Fix 2, Try running:\n~~~\n# oc delete configs.samples cluster\n~~~",
                    'reason': "Due to a temporary hiccup talking to the Red Hat registry the openshift-samples failed to import some of the imagestreams.\n\n\nSource of the issue:\n\n**Cluster-operator:**  **openshift-samples**\n- *Condition:* Degraded\n- *Reason:* FailedImageImports\n- *Message:* Samples installed at 4.2.0, with image import failures for these imagestreams: php \n- *Last* Transition: 2020-03-19T08:32:53Z\n",
                    'description': "Pods could fail to start if openshift-samples is degraded due to FailedImageImport which is caused by a hiccup while talking to the Red Hat registry"
                },
                'namespaces_with_overlapping_uid_ranges|NAMESPACES_WITH_OVERLAPPING_UID_RANGES': {
                    'rule_id': 'ccx_rules_ocp.external.rules.namespaces_with_overlapping_uid_ranges',
                    'error_key': 'NAMESPACES_WITH_OVERLAPPING_UID_RANGES',
                    'resolution': 'Red Hat recommends that you resolve the issue by following the steps in the [Knowledgebase Article](https://access.redhat.com/articles/6844071).',
                    'description': 'Namespaces with collision UID ranges do not meet the compliance requirements with many industry standards',
                    'reason': 'The following namespaces are detected to have collision UID ranges. Namespaces with collision UID ranges do not meet the compliance requirements with many industry standards. In some serious situations, it could lead to data exposure.\n\n\n- Namespaces: \n**openshift**, \n**test-1**, \n**test-2**, \n\n- Namespaces: \n**openshift-ingress-canary**, \n**test-3**, \n\n- Namespaces: \n**test-4**, \n**test-5**, \n**test-6**, \n'
                },
                'cluster_wide_proxy_auth_check|AUTH_OPERATOR_PROXY_ERROR': {
                    'rule_id': 'ccx_rules_ocp.external.rules.cluster_wide_proxy_auth_check',
                    'error_key': 'AUTH_OPERATOR_PROXY_ERROR',
                    'resolution': "Red Hat recommends that you to follow steps in the KCS article.\n * [Authentication operator Degraded with Reason `WellKnownEndpointDegradedError`](https://access.redhat.com/solutions/4569191)\n",
                    'reason': "Requests to routes and/or the public API endpoint are not being proxied to the cluster.\n",
                    'description': "The authentication operator is degraded when cluster is configured to use a cluster-wide proxy"
                }
            }
        }
    }
    rendered = utils.render_reports_v2(data)
    assert rendered == result


def test_render_reports_v2_missing_content():
    """
    Checks that render_reports() function raises exception if the content data are missing.
    """
    data = deepcopy(test_data)
    del data["content"]
    with pytest.raises(ValueError):
        utils.render_reports_v2(data)


def test_render_reports_v2_missing_report_data():
    """
    Checks that render_reports() function raises exception if the report data are missing.
    """
    data = deepcopy(test_data)
    del data["report_data"]
    with pytest.raises(ValueError):
        utils.render_reports_v2(data)


def test_render_reports_v2_missing_clusters():
    """
    Checks that render_reports() function raises exception
    if the data for reported clusters are missing.
    """
    data = deepcopy(test_data)
    del data["report_data"]["clusters"]
    with pytest.raises(ValueError):
        utils.render_reports_v2(data)


def test_render_reports_v2_missing_reports():
    """
    Checks that render_reports() function raises exception
    if the data for individual reports are missing.
    """
    data = deepcopy(test_data)
    del data["report_data"]["reports"]
    with pytest.raises(ValueError):
        utils.render_reports_v2(data)

