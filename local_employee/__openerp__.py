# -*- coding: utf-8 -*-
{
    'name': 'Local Employee',
    'version': '1.3',
    'category': 'Hidden',
    'description': """
The kernel of OpenERP, needed for all installation.
===================================================
""",
    'author': 'OpenERP SA',
    'maintainer': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'depends': ['base','point_of_sale','stock'],
    'data': [
         'local_employee_group.xml',
         'local_employee_user.xml',
         'local_employee_view.xml',
         'security/ir.model.access.csv',
    ],
 
    'installable': True,
    'auto_install': False,
}

