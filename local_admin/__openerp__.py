# -*- coding: utf-8 -*-
{
    'name': 'Local Admin',
    'version': '1.3',
    'category': 'Hidden',
    'description': """
The kernel of OpenERP, needed for all installation.
===================================================
""",
    'author': 'OpenERP SA',
    'maintainer': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'depends': ['base',
                'point_of_sale',
                'purchase',
                'stock',
                'auditlog'],
    'data': [
        'local_admin_group.xml',
        'local_admin_user.xml',
        'local_admin_view.xml',
        'security/ir.model.access.csv',
    ],
 
    'installable': True,
    'auto_install': False,
}

