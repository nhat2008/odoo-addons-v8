# -*- coding: utf-8 -*-
{
    'name': 'Vietnamese Accounting Install',
    'version': '1.3',
    'category': 'Hidden',
    'description': """
The kernel of OpenERP, needed for all installation.
===================================================
""",
    'author': 'COMPANY',
    'maintainer': 'COMPANY',
    'website': 'http://www.company.com',
    'depends': ['base',
                'point_of_sale',
                'l10n_vn'
                ],
    'data': [
        # 'account_data.xml',
        'function_run_one_time.xml',
    ],
 
    'installable': True,
    'auto_install': False,
}

