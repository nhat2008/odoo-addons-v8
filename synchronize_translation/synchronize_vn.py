
import cStringIO

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class base_update_translations(osv.osv_memory):
        _inherit = 'base.update.translations'
        
        def act_update_automatically(self, cr, uid, ids, context=None):
                # _logger.warning("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                # this = self.browse(cr, uid, ids)[0]
                # lang_name = self._get_lang_name(cr, uid, 'vi_VN')
                # _logger.warning(lang_name)
                # _logger.warning(this.lang)
                try:
                        _logger.warning("<<<<<<<<<<<<<<<<<<<< Syn <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                        vn_ids = self.pool['res.lang'].search(cr, uid,[('iso_code','=','vi_VN')],context={})
                        if len(vn_ids) == 0:
                                raise osv.except_osv(_('Error!'), _('No language found'))
                                return {'type': 'ir.actions.act_window_close'}

                        vn_string = self.pool['res.lang'].read(cr, uid, vn_ids, ['name'],context={})[0]
                        _logger.warning(vn_string)
                        _logger.warning("<<<<<<<<<<<<<<<<<<<< Syn <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

                        buf = cStringIO.StringIO()
                        tools.trans_export('vi_VN', ['all'], buf, 'csv', cr)
                        tools.trans_load_data(cr, buf, 'csv', 'vi_VN', lang_name=vn_string['name'])
                        buf.close()
                except:
                        return {'type': 'ir.actions.act_window_close'}

                return {'type': 'ir.actions.act_window_close'}