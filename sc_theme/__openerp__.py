# The manifest file serves to both declare a python package as an Odoo module, and to specify a number of module metadata
{
    # Theme information
    'name': "SC Theme",
    'description': """
    """,
    'category': 'Theme',
    'version': '0.1',
    'depends': ['web', 'point_of_sale'],

    # templates
    'data': [
        'views/login_layout_no_footer.xml',
        'views/left_nav_no_powered_by.xml',
        'views/change_favicon_title.xml',
        'views/change_titles.xml',
    ],
    'qweb': ['static/src/xml/pos_module_changed_logo.xml'],

    # Your information
    'author': "SC developers",
    'website': "",
    
    'installable': True,
    'auto_install': False,
}
