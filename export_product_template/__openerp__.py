{
    'name':'Export product templates',
    'description':'Define some templates for exporting products',
    'author':'Votrongthu',
    'depends':['product_image_filestore_url', 'point_of_sale'],
    'application':True,
    
    'data':['export_product_template.xml',
            'export_productcategory_template.xml',
            'example_product_data.xml',
           ],
}