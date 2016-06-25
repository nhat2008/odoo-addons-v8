# -*- coding: utf-8 -*-

from openerp.osv import fields, osv, orm
from lxml import etree

import logging

_logger = logging.getLogger(__name__)


class res_users(osv.osv):
    _inherit = 'res.users'

    _defaults = {
        'lang': 'vi_VN',
        'tz': "Asia/Ho_Chi_Minh",
    }

    def write(self, cr, uid, ids, vals, context=None):

        # Issue004: Only group base.group_system or user Administrator can modify sel_group in Application
        if any(key.startswith('sel_groups') for key in vals):
            current_user = self.read(cr, uid, uid, ['groups_id'], context=context)
            local_admin_group_id = self.pool['res.groups'].search(cr, uid, [('name', '=', 'Local Admin')])
            if any(id in current_user['groups_id'] for id in local_admin_group_id) and uid != 1:
                raise orm.except_orm(('Access Denied'),
                                     ('You can not change the rights in Application'))


        # Issue004: Auto remove access rights in Application in res.users when changing any fields : in_groups ...
        # Apply for all users except Administrator user, due to Technical feature switch bug
        if any(key.startswith('in_group') for key in vals) and 1 not in ids:
            current_user_groups = self.read(cr, uid, ids, context=context)[0]
            for key in current_user_groups:
                if key.startswith('sel_groups'):
                    vals[key] = False
        # End Issue004

        res = super(res_users, self).write(cr, uid, ids, vals, context=context)
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type="form", context=None, toolbar=False, submenu=False):
        # override of fields_view_get in order to hide some fields groups and the separator accordingly to the shipping type

        if context is None: context = {}

        res = super(res_users, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context,
                                                     toolbar=toolbar, submenu=submenu)

        current_user = self.read(cr, uid, uid, ['groups_id'], context=context)
        local_admin_group_id = self.pool['res.groups'].search(cr, uid, [('name', '=', 'Local Admin')])

        if any(id in current_user['groups_id'] for id in local_admin_group_id) and uid != 1:

            doc = etree.XML(res['arch'])
            
            # Remove all groups in Application
            for node in doc.xpath("//field[contains(@name,'sel_groups')]"):
                node.getparent().remove(node)

            # Remove all groups in Technical Settings, Usability
            local_groups_ids = self.pool['res.groups'].search(cr, uid, [('name', 'ilike', 'Local%')])
            local_groups_ids_string = ['in_group_' + str(group_id) for group_id in local_groups_ids]

            for node in doc.xpath("//field[contains(@name,'in_group_')]"):
                if node.get('name', False) not in local_groups_ids_string:
                    node.getparent().remove(node)

            for node in doc.xpath("//separator[contains(@string,'Application')]"):
                node.getparent().remove(node)
            for node in doc.xpath("//separator[contains(@string,'Technical Settings')]"):
                node.getparent().remove(node)
            for node in doc.xpath("//separator[contains(@string,'Usability')]"):
                node.getparent().remove(node)

            res['arch'] = etree.tostring(doc)

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
