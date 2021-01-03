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
openstackdocs_repo_name = 'openstack/python-neutronclient'
openstackdocs_pdf_link = True
openstackdocs_bug_project = 'python-neutronclient'
openstackdocs_bug_tag = 'doc'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
copyright = 'OpenStack Foundation'

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

# -- Options for LaTeX output ------------------------------------------------

latex_documents = [
    ('index', 'doc-python-neutronclient.tex',
     'python-neutronclient Documentation',
     'Neutron Contributors', 'manual'),
]

# Disable usage of xindy https://bugzilla.redhat.com/show_bug.cgi?id=1643664
latex_use_xindy = False

latex_domain_indices = False

latex_elements = {
    'makeindex': '',
    'printindex': '',
    'preamble': r'\setcounter{tocdepth}{5}',
}

# -- Options for cliff.sphinxext plugin ---------------------------------------

autoprogram_cliff_application = 'openstack'
