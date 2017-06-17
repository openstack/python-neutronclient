# -*- coding: utf-8 -*-
#

import os

import openstackdocstheme


project = 'python-neutronclient'

# -- General configuration ---------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc',
              'reno.sphinxext',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
copyright = u'OpenStack Foundation'

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
html_theme = 'openstackdocs'

html_theme_path = [openstackdocstheme.get_html_theme_path()]

gitsha = os.popen("/usr/bin/git rev-parse HEAD").read()
giturl = ('https://git.openstack.org/cgit/openstack/%s/tree/doc/source'
          % 'python-neutronclient')
html_context = {
    'gitsha': gitsha,
    'giturl': giturl,
    'bug_project': 'python-neutronclient',
    'bug_tag': 'doc',
}
html_last_updated_fmt = os.popen("git log --pretty=format:'%ad' "
                                 "--date=format:'%Y-%m-%d %H:%M' -n1").read()

# Output file base name for HTML help builder.
htmlhelp_basename = '%sdoc' % project


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author,
#  documentclass [howto/manual]).
latex_documents = [
  ('index',
    '%s.tex' % project,
    u'%s Documentation' % project,
    u'OpenStack Foundation', 'manual'),
]
