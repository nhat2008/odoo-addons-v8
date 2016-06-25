# -*- coding: utf-8 -*-
{
    'name': 'POS Order Contraints',
    'version': '1.3',
    'category': 'Hidden',
    'description': """
The kernel of OpenERP, needed for all installation.
===================================================
""",
    'author': 'OpenERP SA',
    'maintainer': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'depends': ['base','point_of_sale', 'stock'],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}

