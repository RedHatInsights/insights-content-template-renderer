import pythonmonkey as pm

from insights_content_template_renderer import DoT
from insights_content_template_renderer.DoT import DEFAULT_TEMPLATE_SETTINGS


DoT_settings = DEFAULT_TEMPLATE_SETTINGS
renderer = DoT.Renderer()


def test_single_quote_correct_handling():
    """
    Checks that DoT template function escapes single quotes
    before creating a JS function out of them.
    """
    template = "An OCP node behaves unexpectedly when it doesn't meet the minimum resource requirements"
    text = pm.eval(f"({renderer.template(template, DoT_settings)})")()
    assert (
        text
        == "An OCP node behaves unexpectedly when it doesn't meet the minimum resource requirements"
    )


def test_nonletter_characters_correct_handling():
    """
    Checks that DoT.template function does not remove characters like
    escape characers and single quotes from the given input if strip is
    set to False
    """
    input = r"Red Hat recommends that you configure your nodes to meet the minimum resource requirements.\n\nMake " \
            r"sure that:\n\n1. Node foo1 (undefined) * Has enough memory, minimum requirement is 16. Currently its " \
            r"only configured with 8.16GB. "

    text = pm.eval(f"({renderer.template(input, DoT_settings._replace(strip = False))})")()
    assert text == input
