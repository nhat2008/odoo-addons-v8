# -*- coding: utf-8 -*-

from openerp.osv import fields, osv, orm

class product_template(osv.Model):
    _inherit = 'product.template'

    _defaults = {
        'type': 'product',
    }