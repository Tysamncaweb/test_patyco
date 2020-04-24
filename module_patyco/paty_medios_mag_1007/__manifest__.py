# coding: utf-8

{
    'name': 'Reporte 1007',
    'version': '1.0',
    'author': 'TYSAMNCA',
    'category': 'Localization colombiana',
    'description': """
    
        Agrega reporte 1007

        Colaborador: Ing. Darrell Sojo
    """,

    'depends': [
        'base_setup',
        'account',
        'paty_comprobante_por_fecha',

    ],
    'data': [
        'wizard/wizard_comprobante_1007.xml',
        'report/report_comprobante_nro1007.xml'        
    ],
    'installable': True,
}
