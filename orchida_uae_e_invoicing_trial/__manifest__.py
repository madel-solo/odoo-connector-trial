{
    'name': 'Orchida UAE E-Invoicing Connector for Odoo | FTA & PINT AE',
    'version': '16.0.1.0.4',
    'summary': 'UAE e-invoicing, UAE e invoicing, UAE e-invoice, UAE e invoice, UAE invoice, UAE invoicing, UAE einvoice, UAE einvoicing',
    'description': """
        Trial/demo module that reproduces the Orchida UAE E-Invoicing
        Connector's screens as UI only.

        It uses the same model names, field names, view XML and XML IDs as
        the full connector, but contains NO core connector logic: no API
        clients, no payload builders, no validator, no credentials, no cron,
        no submission logic. All integration buttons show a message directing
        the user to contact Orchida to activate the full connector.
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
}
