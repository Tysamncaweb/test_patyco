# -*- coding: utf-8 -*-
{
    'name': "Listado de Moviminetos por Comprobantes Patyco",

    'summary': """Listado de Movimientos por Comprobantes Patyco""",

    'description': """
       Listado de Movimientos por Comprobantes Colaborador: Darrell Sojo
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Account',

    # any module necessary for this one to work correctly
    'depends': ['base','account','paty_report_tax'],

    # always loaded
    'data': [
        'wizard/wizard_listado_movimiento.xml',
        'report/template_listado_movimiento.xml'
    ],
    'application': True,
}