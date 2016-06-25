from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, tools
import logging
import base64, urllib
_logger = logging.getLogger(__name__)

class product_template(osv.Model):
    _inherit = "product.template"

    def _get_image(self, cr, uid, ids, name, args, context=None):
        attachment_field = 'image_attachment_id' if name=='image' else 'image_medium_attachment_id'
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'image': obj.image_attachment_id and obj.image_attachment_id.datas or None,
                'image_small': obj.image_small_attachment_id and obj.image_small_attachment_id.datas or None,
                'image_medium': obj.image_medium_attachment_id and obj.image_medium_attachment_id.datas or None,
            }
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        obj = self.browse(cr, uid, id, context=context)
        image_id = obj.image_attachment_id.id
        image_small_id = obj.image_small_attachment_id.id
        image_medium_id = obj.image_medium_attachment_id.id
        if not value:
            ids = [id for id in [image_id, image_small_id, image_medium_id] if id]
            if ids:
                self.pool['ir.attachment'].unlink(cr, uid, ids, context=context)
            return True
        if not (image_id and image_small_id and image_medium_id):
            image_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Product Image'}, context=context)
            image_small_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Product Small Image'}, context=context)
            image_medium_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Product Medium Image'}, context=context)
            self.write(cr, uid, id, {'image_attachment_id': image_id,
                                     'image_small_attachment_id': image_small_id,
                                     'image_medium_attachment_id':image_medium_id},
                       context=context)

        images = tools.image_get_resized_images(value, return_big=True, avoid_resize_medium=True)
        self.pool['ir.attachment'].write(cr, uid, image_id, {'datas': images['image']}, context=context)
        self.pool['ir.attachment'].write(cr, uid, image_small_id, {'datas': images['image_small']}, context=context)
        self.pool['ir.attachment'].write(cr, uid, image_medium_id, {'datas': images['image_medium']}, context=context)
        return True


    # Start Issue015 : Add image url to help in import image from url
    def _check_link(self, link):
       result = False
       if  any(item in link for item in ['.jpg','.png']):
          result = True
       return result

    def _download_image(self, link):
        result = False
        if self._check_link(link):
           try:
              image = urllib.urlopen(link)
              image_size = image.headers['content-length']
              if int(image_size) <= 1048576:
                 result = base64.encodestring(image.read())
           except Exception as e:
              _logger.warning(e)
              result = False
        return result

    def create(self, cr, uid, vals, context=None):
        if context is None:
           context = {}
        # Issue 015: Support import image from link
        if vals.get('image_link', False):
           image_64 = self._download_image(vals['image_link'])
           if image_64:
              vals['image_medium'] = image_64
              vals['image_link'] = ''
        res = super(product_template, self).create(cr, uid, vals, context=context)
        return res


    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
           context = {}
        if vals.get('image_link', False):
           image_64 = self._download_image(vals['image_link'])
           if image_64:
              vals['image_medium'] = image_64
              vals['image_link'] = ''
        res = super(product_template, self).write(cr, uid, ids, vals, context=context)
        return res
     # End Issue015 : Add image url to help in import image from url
    _columns = {
        'image_link': fields.char(string='Image Link'),
        'image_attachment_id': fields.many2one('ir.attachment', 'Image attachment', help='Technical field to store image in filestore'),
        'image_small_attachment_id': fields.many2one('ir.attachment', 'Small-sized Image  attachment', help='Technical field to store image in filestore'),
        'image_medium_attachment_id': fields.many2one('ir.attachment', 'Medium-sized Image  attachment', help='Technical field to store image in filestore'),

        'image': fields.function(_get_image, fnct_inv=_set_image, string="Image", multi='_get_image', type='binary',
            help="This field holds the image used as image for the product, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            help="Medium-sized image of the product. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            help="Small-sized image of the product. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
    }


class product_product(osv.Model):
    _inherit = "product.product"
        
    def _get_image_variant(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        if name == 'image_variant':
            name = 'image'
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image_variant_attachment_id.datas or getattr(obj.product_tmpl_id, name)
        return result

    def _set_image_variant(self, cr, uid, id, name, value, args, context=None):
        obj = self.browse(cr, uid, id, context=context)
        image_variant_id = obj.image_variant_attachment_id.id

        if not value:
            ids = [id for id in [image_variant_id] if id]
            if ids:
                self.pool['ir.attachment'].unlink(cr, uid, ids, context=context)
            return True

        if not image_variant_id:
            image_variant_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Product Variant Image'}, context=context)
            self.write(cr, uid, id, {'image_variant_attachment_id': image_variant_id}, context=context)

        image = tools.image_resize_image_big(value)

        product = self.browse(cr, uid, id, context=context)

        res = self.pool['ir.attachment'].write(cr, uid, image_variant_id, {'datas': image}, context=context)

        if not product.product_tmpl_id.image:
            print ' *** no template image!'
            product.image_variant_attachment_id.unlink()
            product.product_tmpl_id.write({'image': image})
        return res

    _columns = {
        'image_variant_attachment_id': fields.many2one('ir.attachment', 'Image Variant attachment', help='Technical field to store image in filestore',  store=True),

        'image_variant': fields.function(_get_image_variant, fnct_inv=_set_image_variant, string="Variant Image", type='binary',
            help="This field holds the image used as image for the product variant, limited to 1024x1024px."),
        'image': fields.function(_get_image_variant, fnct_inv=_set_image_variant,
            string="Big-sized image", type="binary",
            help="Image of the product variant (Big-sized image of product template if false). It is automatically "\
                 "resized as a 1024x1024px image, with aspect ratio preserved."),
        'image_small': fields.function(_get_image_variant, fnct_inv=_set_image_variant,
            string="Small-sized image", type="binary",
            help="Image of the product variant (Small-sized image of product template if false)."),
        'image_medium': fields.function(_get_image_variant, fnct_inv=_set_image_variant,
            string="Medium-sized image", type="binary",
            help="Image of the product variant (Medium-sized image of product template if false)."),
        'image_link': fields.char(string='Image Link'),
    }
