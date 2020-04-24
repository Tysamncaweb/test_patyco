# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Reportes POS",
    'summary': """Patyco_POS_Report""",

    'description': """
       Reportes en TPV
       Colaborador: Yamile Rayme
    """,
    'version': '12.0.1.0',
    'author': 'Tysamnca',
    'category': 'Tools',
    "version": "12.0.1.0.0",
    "depends": [
        "point_of_sale",
    ],
    "data": [
        "views/pos_templates.xml",
        "views/pos_views.xml",
        "security/ir.model.access.csv",
        "wizard/daily_report_wizard.xml",
        "report/daily_report.xml",
    ],
    "qweb": [
        "static/src/xml/pos.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
