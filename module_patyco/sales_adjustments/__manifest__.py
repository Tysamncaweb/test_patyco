# -*- coding: utf-8 -*-
{
    'name': "submodules/sales_adjustments",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Michel_Castillo/Tysamnca.",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','l10n_co','sale','purchase'],
    'data': ['views/views_sales_adjustments.xml',
         'views/views_sales_adjustments_product.xml',
	 'report/report_sales_adjustments.xml',
	 'report/report_sales_adjustments.xml',
	 'report/report_purchase_adjustments.xml',
     'report/report_invoice_sales_adjustments.xml',
    ],
    # always loaded
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
