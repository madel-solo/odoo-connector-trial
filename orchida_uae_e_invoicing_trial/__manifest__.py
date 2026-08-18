{
    'name': 'Orchida UAE E-Invoicing Connector for Odoo',
    'version': '19.0.1.0.3',
    'summary': 'UAE e-invoicing integration interface for Odoo',
    'description': """
        Trial/demo module showing the Orchida UAE E-Invoicing Connector's
        screens, fields and menus as UI only.

        It contains NO core connector logic: no API clients, no payload
        builders, no validator, no credentials, no submission logic. All
        trial integration buttons show a message directing the user to
        contact Orchida.
    """,
    'author': 'Orchida-Soft',
    'website': 'https://orchidatax.com/e-invoicing-integration-solutions/erp-integrations/odoo',
    'category': 'Accounting',
    'images': ['images/main_screenshot.png'],
    'depends': ['base', 'account', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'security/multi_company_rules.xml',
        'data/unit_code_data.xml',
        'views/api_sent_invoice_view.xml',
        'views/e_invoice_config_form.xml',
        'views/uom_api_map_views.xml',
        'views/account_move_line_view.xml',
        'views/account_journal_view.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/account_tax_view.xml',
        'views/account_move_view.xml',
        'views/product_product_view.xml',
        'views/product_template_view.xml',
        'views/orchida_document_ac_wizard_views.xml',
        'views/menuitems.xml',
        'views/orchida_purchase_invoice_views.xml',
        'views/xml_template.xml',
        'views/xml_pdf_template.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'post_init_hook': 'post_init_hook',
}
