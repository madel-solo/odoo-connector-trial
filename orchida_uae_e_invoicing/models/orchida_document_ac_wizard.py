from odoo import api, fields, models, _
from odoo.exceptions import UserError

from ..constants import UNCL5189_ALLOWANCE_CODES, UNCL7161_CHARGE_CODES
from ..contact import raise_contact_message


class OrchidaDocumentAcWizard(models.TransientModel):
    _name = 'orchida.document.ac.wizard'
    _description = 'Document Allowance/Charge Wizard'

    move_id = fields.Many2one(
        'account.move',
        string='Invoice',
        required=True,
        ondelete='cascade',
    )
    indicator = fields.Selection(
        [('allowance', 'Allowance'), ('charge', 'Charge')],
        string='Type',
        required=True,
    )
    amount = fields.Float(
        string='Amount',
        required=True,
        digits=(16, 2),
        help='Positive amount for the document-level allowance or charge.',
    )
    allowance_reason_code = fields.Selection(
        UNCL5189_ALLOWANCE_CODES,
        string='Allowance Reason Code',
    )
    charge_reason_code = fields.Selection(
        UNCL7161_CHARGE_CODES,
        string='Charge Reason Code',
    )
    reason = fields.Char(
        string='Reason',
        required=True,
    )
    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
        required=True,
        domain="[('type_tax_use', '=', 'sale')]",
        help='Tax applied to this allowance or charge line.',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move_id = self.env.context.get('default_move_id')
        if move_id and 'tax_id' in fields_list:
            move = self.env['account.move'].browse(move_id)
            company = move.company_id
            if company.account_sale_tax_id:
                res['tax_id'] = company.account_sale_tax_id.id
        return res

    def action_confirm(self):
        self.ensure_one()
        raise_contact_message()
