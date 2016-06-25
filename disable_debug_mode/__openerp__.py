# -*- coding: utf-8 -*-
{
    'name': 'Disable Debug Mode ,except Administrator',
    'version': '0.1',
    'category': 'Hidden',
    'description': """
The kernel of OpenERP, needed for all installation.
===================================================
""",
    'author': 'OpenERP SA',
    'maintainer': 'OpenERP SA',
    'website': 'htt://www.openerp.com',
    'depends': ['base'],
    'data': [
    ],
    'qweb' : [
        "static/src/xml/disable_debug.xml",
    ],
    'installable': True,
    'auto_install': False,
}

