# -*- coding: utf-8 -*-

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def create(self, cr, uid, vals ,context=None):
        if vals.get('origin',False):
            invoice_list = self.search(cr, uid, [('number','=',vals['origin'])], context={})
            sale_order_list = self.pool['sale.order'].search(cr, uid, [('name','=',vals['origin'])], context={})
            pos_order_list = self.pool['pos.order'].search(cr, uid, [('name','=',vals['origin'])], context={})
            purchase_order_list = self.pool['purchase.order'].search(cr, uid, [('name','=',vals['origin'])], context={})
            if not (invoice_list or sale_order_list or pos_order_list or purchase_order_list):
                raise osv.except_osv(_('Error!'),_("Can not create a refund without a real invoice!"))	
        result = super(account_invoice, self).create(cr, uid, vals, context=context)
        return result


    def write(self, cr, uid, ids, vals, context=None):
    	current_object = self.read(cr, uid, ids[0], context={})
        if current_object['origin']:
            refund_list = self.search(cr, uid, [('origin','=',current_object['origin']),('type','like','refund')])
            if len(refund_list) > 1:
                raise osv.except_osv(_('Error!'),_("A refund for this invoice have been created already!"))
        result = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
