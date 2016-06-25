import logging
import time
from datetime import datetime

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product

_logger = logging.getLogger(__name__)

class pos_order(osv.osv):
    _inherit = 'pos.order'
    _columns= {
        'pos_order_ref': fields.char('Refund for', readonly=True),
        'one_time': fields.integer('Is Return', readonly=True)
    }
    _defaults = {
             'one_time': 1,
    }

    def refund(self, cr, uid, ids, context=None):
        """Create a copy of order  for refund order"""
        clone_list = []
        line_obj = self.pool.get('pos.order.line')
        
        for order in self.browse(cr, uid, ids, context=context):
            # Check refund
            pos_order_refund = self.pool.get('pos.order').search(cr, uid, [('pos_order_ref', '=', order.name)], context=context)
            if (pos_order_refund or order.pos_order_ref) and hasattr(order, 'one_time'):
                raise osv.except_osv(_('Error!'),_("A refund for this sale order has created already!"))
            # Check refunds
            current_session_ids = self.pool.get('pos.session').search(cr, uid, [('state', '!=', 'closed'),('user_id', '=', uid)], context=context)

            if not current_session_ids:
                raise osv.except_osv(_('Error!'), _('To return product(s), you need to open a session that will be used to register the refund.'))

            clone_id = self.copy(cr, uid, order.id, {
                'name': order.name + ' REFUND', # not used, name forced by create
                'session_id': current_session_ids[0],
                'date_order': time.strftime('%Y-%m-%d %H:%M:%S'),
                'pos_order_ref': order.name or '',
            }, context=context)
            clone_list.append(clone_id)

        for clone in self.browse(cr, uid, clone_list, context=context):
            for order_line in clone.lines:
                line_obj.write(cr, uid, [order_line.id], {
                    'qty': -order_line.qty
                }, context=context)

        abs = {
            'name': _('Return Products'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id':clone_list[0],
            'view_id': False,
            'context':context,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
        return abs

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}

        current_order_object = self.browse(cr, uid, ids, context)
       
        if current_order_object.pos_order_ref and vals.get('lines',False):

            # Check new insert
            for pos_line in vals['lines']:
                # There are : 0 for insert , 1 for editing
                if pos_line[0] == 0:
                    raise osv.except_osv(_('Error!'), _('You can not insert new products to other refunds'))                
            # Check new insert

            # Check new update: can not change price or discount, change the quantity greater than the origin
            check_update = False
            for pos_line in vals['lines']:
                if pos_line[2] and (pos_line[2].get('price_unit',False) or pos_line[2].get('discount',False)):
                    raise osv.except_osv(_('Error!'), _('You can not change the price or the discount of order lines'))

            for pos_line in vals['lines']:
                if pos_line[2] and (pos_line[2].get('qty',False)):
                    pos_order_line_id = pos_line[1]
                    pos_order_line_object = self.pool['pos.order.line'].read(cr, uid, pos_order_line_id,['qty'],context)
                    if (pos_order_line_object['qty']) > (pos_line[2]['qty']): 
                        raise osv.except_osv(_('Error!'), _('You can not change the quantity greater than the origin'))
                    if pos_line[2]['qty'] > 0:
                        raise osv.except_osv(_('Error!'), _('You can not retrun products with negative quantity'))
                        
            # Check new update: can not change price or discount, change the quantity greater than the origin

        res = super(pos_order, self).write(cr, uid, ids, vals, context)
        return res