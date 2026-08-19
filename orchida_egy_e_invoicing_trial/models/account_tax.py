from odoo import fields, models


AETaxCat_CODES = [
    ('S', 'S - Standard rate'),
    ('E', 'E - Exempt from tax'),
    ('O', 'O - Services outside scope of tax'),
    ('AE', 'AE - VAT Reverse Charge'),
    ('Z', 'Z - Zero rated'),
    ('N', 'N - Standard rate additional VAT'),
]


AE_EXEMPTION_CODES = [
    ('DL8.46.1', 'DL8.46.1 - Certain financial services'),
    ('DL8.46.2', 'DL8.46.2 - Supply of residential units (lease or sale)'),
    ('DL8.46.3', 'DL8.46.3 - Bare land'),
    ('DL8.46.4', 'DL8.46.4 - Local passenger transport'),
]

AE_GOODS_TYPE_CODES = [
    ('DL8.48.8.1', 'DL8.48.8.1 - Gold and Diamonds'),
    ('DL8.48.8.2', 'DL8.48.8.2 - Electronic Devices'),
    ('DL8.48.3.1', 'DL8.48.3.1 - Crude or refined oil'),
    ('DL8.48.3.2', 'DL8.48.3.2 - Unprocessed or processed natural gas'),
    ('DL8.48.3.3', 'DL8.48.3.3 - Pure hydrocarbons'),
]


class AccountTax(models.Model):
    _inherit = 'account.tax'

    orchida_tax_category = fields.Selection(
        AETaxCat_CODES,
        string='Orchida PINT AE Tax Category',
        help='UAE PINT AE VAT category code used for e-invoice line tax breakdown.',
    )
    orchida_exemption_code = fields.Selection(
        AE_EXEMPTION_CODES,
        string='Orchida Exemption Code',
        help='Required when tax category is "Exempt from tax" (E).',
    )
    orchida_rcm_goods_type = fields.Selection(
        AE_GOODS_TYPE_CODES,
        string='RCM NatureCode',
        help='Required when tax category is "VAT Reverse Charge" (AE).',
    )

    def seed_default_tax_categories(self):
        pass
