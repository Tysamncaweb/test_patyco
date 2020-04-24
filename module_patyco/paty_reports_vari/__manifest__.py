# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Reporte de Auxiliar General",
    'summary': """Patyco Reporte de Auxiliar General""",

    'description': """
       Reporte de Auxiliar General
       Colaborador: Ing. Yorman Pineda
    """,
    'version': '12.0.1.0',
    'author': 'Tysamnca',
    'category': 'Tools',
    "version": "12.0.1.0.0",
    "depends": [
        "base","account","paty_report_tax",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/report_auxiliar_wizard.xml",
        "report/report_auxiliar.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
