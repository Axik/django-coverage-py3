"""
Copyright 2009 55 Minutes (http://www.55minutes.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import cgi, os

from .data_storage import ModuleVars
from .templates import default_module_detail as module_detail

def html_module_detail(filename, module_name, nav=None):
    """
    Creates a module detail report based on coverage testing at the specified
    filename. If ``nav`` is specified, the nav template will be used as well.

    It uses `templates.default_module_detail` to create the page. The template
    contains the following sections which need to be rendered and assembled into
    the final HTML.

    TOP: Contains the HTML declaration and head information, as well as the
         inline stylesheet. It requires the following variable:
         * %(title)s The module name is probably fitting for this.

    CONTENT_HEADER: The header portion of the body. Requires the following variable:
                    * %(title)s
                    * %(source_file)s File path to the module
                    * %(total_count)d
                    * %(executed_count)d
                    * %(excluded_count)d
                    * %(ignored_count)d
                    * %(percent_covered)0.1f
                    * %(test_timestamp)s

    CONTENT_BODY: Annotated module source code listing. Requires the following variable:
                  * ``%(source_lines)s`` The actual source listing which is generated by
                    looping through each line and concatenanting together rendered
                    ``SOURCE_LINE`` template (see below).

    BOTTOM: Just a closing ``</body></html>``

    SOURCE_LINE: Used to assemble the content of ``%(source_lines)s`` for ``CONTENT_BODY``.
                 Requires the following variables:
                 * ``%(line_status)s`` (ignored, executed, missed, excluded) used as CSS class
                   identifier to style the each source line.
                 * ``%(source_line)s``
    """
    if not nav:
        nav = {}
    m_vars = ModuleVars(module_name)

    m_vars.source_lines = source_lines = list()
    i = 0
    for i, source_line in enumerate(
        [cgi.escape(l.rstrip()) for l in file(m_vars.source_file, 'rb').readlines()]):
        line_status = 'ignored'
        if i+1 in m_vars.executed: line_status = 'executed'
        if i+1 in m_vars.excluded: line_status = 'excluded'
        if i+1 in m_vars.missed: line_status = 'missed'
        source_lines.append(module_detail.SOURCE_LINE %vars())
    m_vars.ignored_count = i+1 - m_vars.total_count
    m_vars.source_lines = os.linesep.join(source_lines)

    if 'prev_link' in nav and 'next_link' in nav:
        nav_html = module_detail.NAV %nav
    elif 'prev_link' in nav:
        nav_html = module_detail.NAV_NO_NEXT %nav
    elif 'next_link' in nav:
        nav_html = module_detail.NAV_NO_PREV %nav
    else:
        nav_html = None

    fo = file(filename, 'wb+')
    print >>fo, module_detail.TOP %m_vars.__dict__
    if nav and nav_html:
        print >>fo, nav_html
    print >>fo, module_detail.CONTENT_HEADER %m_vars.__dict__
    print >>fo, module_detail.CONTENT_BODY %m_vars.__dict__
    if nav and nav_html:
        print >>fo, nav_html
    print >>fo, module_detail.BOTTOM
    fo.close()

