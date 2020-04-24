# -*- coding: utf-8 -*-
{
    'name': "Listado de Comprobantes Patyco xx",

    'summary': """Listado de Comprobantes Patyco""",

    'description': """
       Listado de Comprobantes
       Colaborador: Darrell Sojo
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Account',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'report/plantilla_listado_comprobante.xml'
    ],
    'application': True,
}