# -*- coding: utf-8 -*-
{
    'name': "Configuracion reportes medios Magneticos",

    'summary': """Configuracion reportes medios Magneticos""",

    'description': """
       Configuracion reportes medios Magneticos
       Colaborador: Ing. Darrell Sojo
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',        
        'view/vista_formato.xml',
        'view/vista_conceptos.xml',
        'view/vista_medios_magneticos.xml',
        'view/vista_cod_pais.xml',
        'view/vista_cod_departamento.xml',
        'view/vista_cod_municipio.xml',
        'view/vista_menu.xml',
        'view/vista_partner.xml'
    ],
    'application': True,
}
