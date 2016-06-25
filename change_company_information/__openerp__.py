# -*- coding: utf-8 -*-
{
    'name': 'Change Company Information',
    'version': '1.3',
    'category': 'Hidden',
    'description': """
The kernel of OpenERP, needed for all installation.
===================================================
""",
    'author': 'OpenERP SA',
    'maintainer': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'depends': ['base'],
    'data': [
         'change_company_information.xml',
    ],
 
    'installable': True,
    'auto_install': False,
}