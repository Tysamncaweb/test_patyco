# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Reporte Genérico de Impuestos",
    'summary': """Patyco Reporte Genérico de Impuestos""",

    'description': """
       Reporte Genérico de Impuestos
       Colaborador: Yamile Rayme
    """,
    'version': '12.0.1.0',
    'author': 'Tysamnca',
    'category': 'Tools',
    "version": "12.0.1.0.0",
    "depends": [
        "base","account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/report_tax_wizard.xml",
        "report/report_tax.xml",
    ],

    "installable": True,
    #"post_init_hook": "post_init_hook",
    #"uninstall_hook": "uninstall_hook",
}
