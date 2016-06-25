{
    'name':'Audit Logging rules',
    'description':'Define some rules for auditlog module',
    'author':'TriTruong',
    'depends':['product','auditlog'],
    'application':True,
    
    'data':['audit_logging_rule.xml'],

    'installable': True,
    'auto_install': False,
}