# MIT License
#
# Copyright (c) 2022 David Chen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module implements the DoT.js template framework in Python.
Source: https://github.com/lucemia/doT
"""

import doT
import logging

log = logging.getLogger(__name__)

version = "1.0.0"

DEFAULT_TEMPLATE_SETTINGS = doT.TemplateSettings()
DEFAULT_TEMPLATE_SETTINGS = DEFAULT_TEMPLATE_SETTINGS._replace(
    varname = "pydata"
)

class Renderer:
    """Class encapsulating logic of rendering DoT.js templates."""
    def template(self, tmpl, c=None, _def=None):
        return doT.template(tmpl, c, _def)
