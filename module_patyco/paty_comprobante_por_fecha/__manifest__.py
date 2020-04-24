# coding: utf-8

{
    'name': 'Reporte Comprobantes Contables por Fecha',
    'version': '1.0',
    'author': 'TYSAMNCA',
    'category': 'Localization colombiana',
    'description': """
    
        Agrega reporte de comprobantes contables por fecha

        Colaborador: Nathaly Partidas
    """,

    'depends': [
        'base_setup',
        'account',

    ],
    'data': [
        'wizard/wizard_comprobante_por_fecha.xml',
        'report/report_comprobante_contable.xml'


    ],
    'installable': True,
}
