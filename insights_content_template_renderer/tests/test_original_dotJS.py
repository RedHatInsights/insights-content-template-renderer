import doT
from insights_content_template_renderer.DoT import Renderer

input = """
{{?pydata.test.length>1
}}First if{{?? pydata.test[0]['subtest'].length>1
}}Second if{{??
}}Third if{{?}}.

More text
"""

want = "function anonymous(it) {var out='';if(pydata.test.length>1){out+='First if';}else if(pydata.test[0]['subtest'].length>1){out+='Second if';}else{out+='Third if';}out+='.More text';return out;}"

def test_dotJS_newline():
    assert doT.template(input) == want

def test_our_dotJS_newline():
    r = Renderer()
    assert r.template(input) == want
