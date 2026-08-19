from odoo import api, fields, models


DEFAULT_UOM_MAPPINGS = (
    ('uom.product_uom_millimeter', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_mmt'),
    ('uom.product_uom_gram', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_grm'),
    ('uom.product_uom_cm', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_cmt'),
    ('uom.product_uom_cubic_inch', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_inq'),
    ('uom.product_uom_inch', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_inh'),
    ('uom.product_uom_oz', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_onz'),
    ('uom.product_uom_floz', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_oza'),
    ('uom.uom_square_foot', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_ftk'),
    ('uom.product_uom_hour', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_hur'),
    ('uom.product_uom_foot', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_fot'),
    ('uom.product_uom_lb', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_lbr'),
    ('uom.product_uom_yard', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_yrd'),
    ('uom.product_uom_qt', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_qtl'),
    ('uom.product_uom_unit', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_c62'),
    ('uom.product_uom_day', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_day'),
    ('uom.product_uom_meter', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_mtr'),
    ('uom.uom_square_meter', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_mtk'),
    ('uom.product_uom_litre', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_ltr'),
    ('uom.product_uom_kgm', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_kgm'),
    ('uom.product_uom_gal', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_gll'),
    ('uom.product_uom_dozen', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_dzn'),
    ('uom.product_uom_cubic_foot', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_ftq'),
    ('uom.product_uom_km', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_kmt'),
    ('uom.product_uom_cubic_meter', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_mtq'),
    ('uom.product_uom_ton', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_tne'),
    ('uom.product_uom_mile', 'orchida_ksa_e_invoicing_trial.orchida_unit_code_smi'),
)


class OrchidaUomApiMap(models.Model):
    _name = 'orchida.uom.api.map'
    _description = 'Orchida UoM to API UnitCode Mapping'
    _order = 'company_id, uom_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='UoM',
        required=True,
        index=True,
        help='Odoo Unit of Measure to map into invoice line UnitCode.',
    )
    unit_code_id = fields.Many2one(
        'orchida.unit.code',
        string='API UnitCode',
        required=True,
        index=True,
        help='Select UN/ECE Rec 20 + Rec 21 unit code used for line UnitCode (for example: EA).',
    )
    active = fields.Boolean(default=True)

    @api.model
    def seed_default_mappings(self):
        return

    _sql_constraints = [
        ('uniq_company_uom_map', 'unique(company_id, uom_id)', 'A UnitCode mapping for this UoM already exists for this company.'),
    ]
