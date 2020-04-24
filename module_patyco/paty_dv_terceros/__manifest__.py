# -*- coding: utf-8 -*-
{
    'name': "Patyco Localización funcional terceros",

    'summary': """patyco terceros""",

    'description': """
      Este módulo incluye el Dígito de verificación (dv), Apellidos y Nombres
Colaboradores: Yamile Rayme
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly.
    'depends': ['base', 'account',],

    # always loaded
    'data': [
        'views/dv_terceros.xml',
    ],

    "installable": True,
    #"post_init_hook": "post_init_hook",
    #"uninstall_hook": "uninstall_hook",
}
