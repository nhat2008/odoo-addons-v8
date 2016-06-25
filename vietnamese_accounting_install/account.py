# -*- coding: utf-8 -*-

from openerp.osv import fields, osv, orm
from lxml import etree
from openerp import SUPERUSER_ID
from datetime import datetime
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta


class wizard_multi_charts_accounts(osv.osv_memory):
    _inherit = 'wizard.multi.charts.accounts'

    def execute_automatically(self, cr, uid, ids, context=None):
        '''
        This function is called at the confirmation of the wizard to generate the COA from the templates. It will read
        all the provided information to create the accounts, the banks, the journals, the taxes, the tax codes, the
        accounting properties... accordingly for the chosen company.
        ''' 
        input_company_id = 1
        # Get chart of account template : VN - Chart of Accounts
        input_COA_template_id = self.pool['account.chart.template'].search(cr, uid, [('name','=','VN - Chart of Accounts')])
        input_currency_id = self.pool['res.currency'].search(cr, uid, [('name','=','VND')])
        input_code_digits = 6
        input_sale_tax = self.pool['account.tax.template'].search(cr, uid, [('name','=',u'Thuế GTGT phải nộp 0%')])
        input_purchase_tax = self.pool['account.tax.template'].search(cr, uid, [('name','=',u'Thuế GTGT được khấu trừ 0%')])


        if not input_COA_template_id:
            return {}
        new_id = self.create(cr, uid, {'company_id':input_company_id, 'chart_template_id':input_COA_template_id[0], 'currency_id': input_currency_id[0], 
                                        'code_digits':input_code_digits, 'sale_tax':input_sale_tax[0], 'purchase_tax':input_purchase_tax[0]}, context={})

        
        obj_data = self.pool.get('ir.model.data')
        ir_values_obj = self.pool.get('ir.values')
        obj_wizard = self.browse(cr, uid, new_id)
        company_id = obj_wizard.company_id.id

        self.pool.get('res.company').write(cr, uid, [company_id], {'currency_id': obj_wizard.currency_id.id})

        # When we install the CoA of first company, set the currency to price types and pricelists
        if company_id==1:
            for ref in (('product','list_price'),('product','standard_price'),('product','list0'),('purchase','list0')):
                try:
                    tmp2 = obj_data.get_object_reference(cr, uid, *ref)
                    if tmp2: 
                        self.pool[tmp2[0]].write(cr, uid, tmp2[1], {
                            'currency_id': obj_wizard.currency_id.id
                        })
                except ValueError:
                    pass

        # If the floats for sale/purchase rates have been filled, create templates from them
        self._create_tax_templates_from_rates(cr, uid, obj_wizard, company_id, context=context)

        # Install all the templates objects and generate the real objects
        acc_template_ref, taxes_ref, tax_code_ref = self._install_template(cr, uid, obj_wizard.chart_template_id.id, company_id, code_digits=obj_wizard.code_digits, obj_wizard=obj_wizard, context=context)

        # write values of default taxes for product as super user
        if obj_wizard.sale_tax and taxes_ref:
            ir_values_obj.set_default(cr, SUPERUSER_ID, 'product.template', "taxes_id", [taxes_ref[obj_wizard.sale_tax.id]], for_all_users=True, company_id=company_id)
        if obj_wizard.purchase_tax and taxes_ref:
            ir_values_obj.set_default(cr, SUPERUSER_ID, 'product.template', "supplier_taxes_id", [taxes_ref[obj_wizard.purchase_tax.id]], for_all_users=True, company_id=company_id)

        # Create Bank journals
        self._create_bank_journals_from_o2m(cr, uid, obj_wizard, company_id, acc_template_ref, context=context)
        return {}

class account_fiscalyear(osv.osv):
    _inherit = "account.fiscalyear"

    def create_period_automatically(self, cr, uid, ids, context=None, interval=1):
        fiscal_year_data_ids = self.search(cr, uid, [], context={})
        period_obj = self.pool.get('account.period')
        for fy in self.browse(cr, uid, fiscal_year_data_ids, context=context):
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            period_obj.create(cr, uid, {
                    'name':  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
                    'code': ds.strftime('00/%Y'),
                    'date_start': ds,
                    'date_stop': ds,
                    'special': True,
                    'fiscalyear_id': fy.id,
                })
            while ds.strftime('%Y-%m-%d') < fy.date_stop:
                de = ds + relativedelta(months=interval, days=-1)

                if de.strftime('%Y-%m-%d') > fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                period_obj.create(cr, uid, {
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
