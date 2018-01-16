# -*- coding: utf-8 -*-
#

# -- General configuration ---------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'reno.sphinxext',
    'openstackdocstheme',
    'cliff.sphinxext',
]

# openstackdocstheme options
repository_name = 'openstack/python-neutronclient'
bug_project = 'python-neutronclient'
bug_tag = 'doc'
html_last_updated_fmt = '%Y-%m-%d %H:%M'

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

# Output file base name for HTML help builder.
htmlhelp_basename = 'neutronclientdoc'

# -- Options for cliff.sphinxext plugin ---------------------------------------

autoprogram_cliff_application = 'openstack'
