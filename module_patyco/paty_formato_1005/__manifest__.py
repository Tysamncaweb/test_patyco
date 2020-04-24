# -*- coding: utf-8 -*-
{
    'name': "Formato de medios magneticos 1005",

    'summary': """Formato de medios magneticos 1005
                  Colaborador: Nathaly Partidas""",

    'description': """
       Formato de medios magneticos 1005
       Colaborador: Nathaly Partidas
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Account',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'wizard/wizard_formato_1005.xml',
        'report/template_formato_1005.xml',
        'view/config_formato_1005.xml',
        'security/ir.model.access.csv'
    ],
    'application': True,
}