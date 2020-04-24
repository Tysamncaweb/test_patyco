# -*- coding: utf-8 -*-
{
    'name': "Inclusion del campo correlativo",

    'summary': """Inclusion del campo correlativo de los Diarios""",

    'description': """
       Inclusion del campo correlativo de los Diarios
       Colaborador: Nathaly Partidas
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Account',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'view/account_journal_view.xml'
    ],
    'application': True,
}
