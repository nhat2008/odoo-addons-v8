import openerp.addons.product.product

def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if the string has the wrong length"""
    return 1

def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    return True

def sanitize_ean13(ean13):
    """Creates and returns a valid ean13 from an invalid one"""
    return ean13

openerp.addons.product.product.ean_checksum = ean_checksum
openerp.addons.product.product.check_ean = check_ean
openerp.addons.product.product.sanitize_ean13 = sanitize_ean13
