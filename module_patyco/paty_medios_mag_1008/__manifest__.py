# coding: utf-8

{
    'name': 'Reporte 1008 y 1009',
    'version': '1.0',
    'author': 'TYSAMNCA',
    'category': 'Localization Colombiana',
    'description': """
    
        Agrega Reporte 1008 y 1009

        Colaborador: Ing. Darrell Sojo
    """,

    'depends': [
        'base_setup',
        'account',
        'paty_comprobante_por_fecha',
        'paty_config_medios_mag',
        'paty_medios_mag_1007',

    ],
    'data': [
        'wizard/wizard_comprobante_1008.xml'          
    ],
    'installable': True,
}
