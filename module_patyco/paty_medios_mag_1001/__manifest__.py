# coding: utf-8

{
    'name': 'Reporte 1001',
    'version': '1.0',
    'author': 'TYSAMNCA',
    'category': 'Localization Colombiana',
    'description': """
    
        Agrega Reporte 1001 - Pagos y abonos en cuenta y Retenciones practicadas

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
        'wizard/wizard_retenciones_1001.xml'          
    ],
    'installable': True,
}
