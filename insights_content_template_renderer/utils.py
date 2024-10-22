"""
Provides all business logic for this service.
"""

import logging
import re
from typing import List

from insights_content_template_renderer import DoT
from insights_content_template_renderer.DoT import DEFAULT_TEMPLATE_SETTINGS
from insights_content_template_renderer.models import RendererRequest, \
    RendererResponse, RenderedReport, Content, Report

from js2py import eval_js

DoT_settings = DEFAULT_TEMPLATE_SETTINGS
log = logging.getLogger(__name__)
renderer = DoT.Renderer()


class RuleNotFoundException(Exception):
    """
    Exception raised if the content data for reported module do not exist.
    """


class TemplateNotFoundException(Exception):
    """
    Exception raised if the template for given reported module
    and field name ('reason'/'resolution') does not exist.
    """


def get_reported_module(report: Report) -> str:
    """
    Returns the name of the reported module.

    :param report: dictionary with report details
    :return: name of the reported module
    """
    return report.component[0 : report.component.rfind(".")]


def get_reported_error_key(report: Report) -> str:
    """
    Returns the reported error key.

    :param report: dictionary with report details
    :return: reported error key
    """
    return report.key


def escape_raw_text_for_js(text):
    """
    Escapes all the escape characters like whitespace, newline, tabulation,
    etc, as well as single quotes.
    """
    return text.encode("unicode_escape").decode()


def escape_new_line_inside_brackets(text):
    """
    Escape the new lines inside brackets that were causing some issues.
    https://issues.redhat.com/browse/CCXDEV-10314
    """
    return re.sub(r'{{(.*?)\\n}}', r'{{\1}}', text)


def unescape_raw_text_for_python(text):
    """
    Undoes all the escaping of special characters like whitespace, newline, tabulation,
    etc, as well as single quotes.
    """
    return text.encode().decode('unicode-escape')


def get_template_function(template_name, template_text, report: Report):
    """
    Retrieves the DoT.js template based on the name of the field in the given content data
    and returns the Python function created with that template.

    :param template_name: name of the field in content data with template
    :param template_text: template in DoT.js format
    :param report: dictionary with report details
    :return: Python function for rendering report based on given report details
    """
    if template_text is None or template_text == "":
        reported_module = get_reported_module(report)
        reported_error_key = get_reported_error_key(report)
        raise TemplateNotFoundException(
            f"Template '{template_name}' has not been found for rule '{reported_module}' "
            + f"and error key '{reported_error_key}'."
        )

    template_text_no_newline_inside_brackets = escape_new_line_inside_brackets(
        escape_raw_text_for_js(template_text)
    )

    template = renderer.template(
        template_text_no_newline_inside_brackets,
        DoT_settings
    )
    return eval_js(template)


def render_description(rule_content: Content, report: Report):
    """
    Renders report description.

    :param rule_content: dictionary with content data for reported rule
    :param report: dictionary with report details
    :return: string with rendered description
    """
    reported_error_key = get_reported_error_key(report)
    error_key_content = rule_content.error_keys[reported_error_key]

    if (
        "description" in error_key_content["metadata"]
        and error_key_content["metadata"]["description"]
    ):
        template_text = error_key_content["metadata"]["description"]

    try:
        description_template = get_template_function(
            "metadata.description", template_text, report
        )
    except TemplateNotFoundException:
        return ""
    return unescape_raw_text_for_python(description_template(report.details))


def render_resolution(rule_content: Content, report: Report):
    """
    Renders report resolution.

    :param rule_content: dictionary with content data for reported rule
    :param report: dictionary with report details
    :return: string with rendered resolution
    """
    template_text = rule_content.resolution

    reported_error_key = get_reported_error_key(report)
    error_key_content = rule_content.error_keys[reported_error_key]

    if "resolution" in error_key_content and error_key_content["resolution"]:
        template_text = error_key_content["resolution"]

    try:
        resolution_template = get_template_function("resolution", template_text, report)
    except TemplateNotFoundException:
        return ""
    return unescape_raw_text_for_python(resolution_template(report.details))


def render_reason(rule_content: Content, report: Report):
    """
    Renders report reason.

    :param rule_content: dictionary with content data for reported rule
    :param report: dictionary with report details
    :return: string with rendered reason
    """
    template_text = rule_content.reason

    reported_error_key = get_reported_error_key(report)
    error_key_content = rule_content.error_keys[reported_error_key]

    if "reason" in error_key_content and error_key_content["reason"]:
        template_text = error_key_content["reason"]

    try:
        reason_template = get_template_function("reason", template_text, report)
    except TemplateNotFoundException:
        return ""
    return unescape_raw_text_for_python(reason_template(report.details))


def render_report(content: List[Content], report: Report) -> RenderedReport:
    """
    Renders the given report.

    :param content: list with content data for all rules
    :param report: dictionary with report details
    :return: rendered report
    """
    try:
        reported_module = get_reported_module(report)
        reported_error_key = get_reported_error_key(report)
    except ValueError as exception:
        raise exception

    for rule in content:
        if reported_module == rule.plugin["python_module"]:
            report_result = RenderedReport(
                rule_id = reported_module,
                error_key = reported_error_key,
                resolution = render_resolution(rule, report),
                reason = render_reason(rule, report),
                description = render_description(rule, report),
            )
            return report_result

    msg = f"The rule content for '{reported_module}' has not been found."
    raise RuleNotFoundException(msg)


def render_reports(request_data: RendererRequest) -> RendererResponse:
    """
    Renders all reports and returns dictionary with the rendered results.

    :param request_data: dictionary retrieved from JSON body of the request
    :return: rendered reports
    """
    log.info("Loading content and report data")

    content = request_data.content
    report_data = request_data.report_data
    result = RendererResponse(
        clusters = report_data.clusters,
        reports = {}
    )

    log.info("Iterating through the reports of each cluster")

    for cluster_id, cluster_data in report_data.reports.items():
        for report in cluster_data.reports:
            try:
                report_result = render_report(content, report)
                result.reports.setdefault(cluster_id, []).append(report_result)
            except (
                ValueError,
                RuleNotFoundException,
                TemplateNotFoundException,
            ) as exception:
                log.debug(exception)
                log.debug(
                    "The report for rule '%s' and error key '%s' could not be processed.",
                    get_reported_module(report),
                    get_reported_error_key(report),
                )

    log.info("The reports from the request have been processed")

    return result
