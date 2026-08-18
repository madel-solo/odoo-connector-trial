from odoo import api, fields, models, _
from odoo.exceptions import UserError

from ..contact import raise_contact_message

CREDIT_NOTE_REASONS = {
    'DL8.61.1.A': 'If the supply was cancelled.',
    'DL8.61.1.B': 'If the tax treatment of the supply has changed due to a change in the nature of the supply.',
    'DL8.61.1.C': 'If the previously agreed consideration for the supply was altered for any reason (i.e. bad debt relief).',
    'DL8.61.1.D': 'If the recipient of goods or recipient of services returned them to the registrant in full or in part and the Consideration was returned in full or in part.',
    'DL8.61.1.E': 'If the tax was charged or tax treatment was applied in error.',
    'VD': 'Volume Discount.',
}


class AccountMove(models.Model):
    _inherit = "account.move"

    orchida_send_attempt_ids = fields.One2many(
        'api.sent.invoice',
        'move_id',
        string='Orchida Send Attempts',
    )
    orchida_original_invoice_id = fields.Many2one(
        'account.move',
        string='Original Invoice',
        copy=False,
        check_company=True,
    )
    orchida_submission_state = fields.Selection(
        [
            ('not_applicable', 'Not Applicable'),
            ('to_send', 'To Submit'),
            ('failed', 'Action Required'),
            ('unknown', 'Processing'),
            ('valid', 'Valid'),
        ],
        string='E-Invoice Submission',
        compute='_compute_orchida_submission_state',
        store=True,
        index=True,
    )
    orchida_submission_failure_type = fields.Selection(
        [
            ('document', 'Document'),
            ('configuration', 'Configuration'),
            ('technical', 'Technical'),
        ],
        string='E-Invoice Failure Type',
        compute='_compute_orchida_submission_state',
        store=True,
        readonly=True,
    )

    @api.depends(
        'state',
        'move_type',
        'journal_id.orchida_submit_einvoice',
        'orchida_send_attempt_ids.outcome',
        'orchida_send_attempt_ids.success',
        'orchida_send_attempt_ids.sent_date',
        'orchida_send_attempt_ids.failure_type',
    )
    def _compute_orchida_submission_state(self):
        for move in self:
            if move.state != 'posted' or not move._orchida_should_submit_einvoice():
                move.orchida_submission_state = 'not_applicable'
                move.orchida_submission_failure_type = False
                continue
            attempts = move.orchida_send_attempt_ids.sorted('id')
            if any(attempt.outcome == 'valid' for attempt in attempts):
                move.orchida_submission_state = 'valid'
                move.orchida_submission_failure_type = False
            elif not attempts:
                move.orchida_submission_state = 'to_send'
                move.orchida_submission_failure_type = False
            else:
                latest = attempts[-1]
                move.orchida_submission_state = (
                    'unknown' if latest.outcome == 'unknown' else 'failed'
                )
                move.orchida_submission_failure_type = latest.failure_type

    def _orchida_get_buyer_tax_id(self):
        """Buyer tax ID for e-invoice payload (overridable by bridge modules)."""
        self.ensure_one()
        partner = self.partner_id
        vat = (getattr(partner, 'vat', False) or "").strip()
        if vat:
            return vat
        return (partner.trn_tin or "").strip() or False

    def _orchida_get_buyer_endpoint_id(self):
        """Buyer Endpoint ID for e-invoice payload (overridable by bridge modules)."""
        self.ensure_one()
        return (self.partner_id.buyer_endpoint_id or "").strip() or False

    def _extract_missing_uom_errors(self, errors):
        return [error for error in (errors or []) if error.startswith("Missing UnitCode mapping for UoM:")]

    def _raise_missing_uom_mapping_error(self, errors):
        raise_contact_message()

    amount_orchida_allowance_total = fields.Monetary(
        string='Doc Allowances',
        compute='_compute_orchida_ac_totals',
        store=False,
        help='Sum of document-level allowance lines (absolute value).',
    )
    amount_orchida_charge_total = fields.Monetary(
        string='Doc Charges',
        compute='_compute_orchida_ac_totals',
        store=False,
        help='Sum of document-level charge lines (absolute value).',
    )

    orchida_document_scope = fields.Selection(
        [('standard', 'Standard'), ('out_of_scope', 'Out of scope')],
        string='E-Invoice Document Scope',
        default='standard',
        copy=False,
    )
    orchida_is_free_trade_zone = fields.Boolean(string='Free Trade Zone', copy=False)
    orchida_is_export = fields.Boolean(string='Export', copy=False)
    orchida_is_ecommerce = fields.Boolean(string='E-commerce supply', copy=False)
    orchida_beneficiary_id = fields.Char(string='FTZ Beneficiary ID', copy=False)
    orchida_credit_note_reason_code = fields.Selection(
        [(code, f'{code} - {desc}') for code, desc in sorted(CREDIT_NOTE_REASONS.items())],
        string='Credit Note Reason',
        copy=False,
    )
    orchida_payment_code = fields.Selection(
        [
            ('10', '10 - Cash'),
            ('30', '30 - Bank transfer'),
        ],
        string='Resolved E-Invoice Payment',
        compute='_compute_orchida_payment_code',
        readonly=True,
        copy=False,
    )
    orchida_rcm_readiness = fields.Char(
        string='RCM Readiness',
        compute='_compute_orchida_rcm_readiness',
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reversed_entry_id') and not vals.get('orchida_original_invoice_id'):
                vals['orchida_original_invoice_id'] = vals['reversed_entry_id']
        return super().create(vals_list)

    @api.constrains('orchida_original_invoice_id', 'move_type', 'partner_id', 'company_id')
    def _check_orchida_original_invoice(self):
        for move in self.filtered('orchida_original_invoice_id'):
            original = move.orchida_original_invoice_id
            if move.move_type == 'out_refund' and (
                original.move_type != 'out_invoice'
                or original.state != 'posted'
                or original.company_id != move.company_id
                or original.partner_id != move.partner_id
            ):
                raise UserError(_(
                    'Original Invoice must be a posted customer invoice for the same customer and company.'
                ))

    @api.depends('partner_id.orchida_payment_instruction')
    def _compute_orchida_payment_code(self):
        for move in self:
            override = move.partner_id.orchida_payment_instruction if move.partner_id else False
            move.orchida_payment_code = {'cash': '10', 'credit_transfer': '30'}.get(override, False)

    @api.depends(
        'invoice_line_ids.tax_ids.orchida_tax_category',
        'invoice_line_ids.product_id',
        'invoice_line_ids.product_id.barcode',
        'invoice_line_ids.product_id.orchida_standard_id',
        'invoice_line_ids.product_id.product_tmpl_id.orchida_hs_code',
        'invoice_line_ids.product_id.product_tmpl_id.orchida_sac_code',
    )
    def _compute_orchida_rcm_readiness(self):
        for move in self:
            rcm_lines = move.invoice_line_ids.filtered(
                lambda line: any(tax.orchida_tax_category == 'AE' for tax in line.tax_ids)
            )
            if not rcm_lines:
                move.orchida_rcm_readiness = 'Not applicable'
                continue
            missing = []
            for line in rcm_lines:
                product = line.product_id
                if not (product.barcode or product.orchida_standard_id):
                    missing.append('GTIN')
                item_type = product.product_tmpl_id.orchida_rcm_item_type
                if item_type in ('G', 'B') and not product.product_tmpl_id.orchida_hs_code:
                    missing.append('HS')
                if item_type in ('S', 'B') and not product.product_tmpl_id.orchida_sac_code:
                    missing.append('SAC')
            move.orchida_rcm_readiness = 'Ready' if not missing else 'Incomplete: ' + ', '.join(sorted(set(missing)))

    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.orchida_is_document_ac', 'invoice_line_ids.orchida_ac_indicator')
    def _compute_orchida_ac_totals(self):
        for move in self:
            allowance = 0.0
            charge = 0.0
            for line in move.invoice_line_ids:
                if line.orchida_is_document_ac:
                    amt = abs(line.price_subtotal)
                    if line.orchida_ac_indicator == 'allowance':
                        allowance += amt
                    elif line.orchida_ac_indicator == 'charge':
                        charge += amt
            move.amount_orchida_allowance_total = allowance
            move.amount_orchida_charge_total = charge

    def _get_or_create_orchida_doc_ac_product(self, indicator):
        raise_contact_message()

    def action_add_document_allowance_line(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Add Document Allowance'),
            'res_model': 'orchida.document.ac.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_id': self.id,
                'default_indicator': 'allowance',
            },
        }

    def action_add_document_charge_line(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Add Document Charge'),
            'res_model': 'orchida.document.ac.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_id': self.id,
                'default_indicator': 'charge',
            },
        }

    def action_open_orchida_uom_mapping(self):
        self.ensure_one()
        action = self.env.ref('orchida_uae_e_invoicing_trial.action_orchida_uom_api_map').read()[0]
        action['domain'] = [('company_id', '=', self.company_id.id)]
        action['context'] = {
            'default_company_id': self.company_id.id,
            'search_default_company_id': self.company_id.id,
        }
        return action

    def _orchida_should_submit_einvoice(self):
        """True when this move participates in Orchida e-invoicing."""
        self.ensure_one()
        return (
            self.move_type in ("out_invoice", "out_refund")
            and bool(self.journal_id.orchida_submit_einvoice)
        )

    @api.constrains('amount_total', 'state', 'move_type')
    def _check_orchida_negative_total(self):
        for move in self:
            if (
                move.state == 'posted'
                and move._orchida_should_submit_einvoice()
                and move.move_type == 'out_invoice'
                and move.amount_total < 0
                and not self.env.context.get('bypass_negative_total_check')
            ):
                raise UserError(_(
                    "Invoice total is negative (%(amt)s). "
                    "Please check Document Allowance/Charge lines.",
                    amt=move.amount_total,
                ))

    def _orchida_format_validation_errors(self, errors):
        return "\n".join(f"- {error}" for error in (errors or []))

    def action_post(self):
        return super().action_post()

    def _record_send_result(self, move, result, source):
        raise_contact_message()

    def _orchida_submit_invoice(self, move):
        raise_contact_message()

    def _orchida_failed_submission_result(self, move, message):
        raise_contact_message()

    def action_orchida_send(self):
        raise_contact_message()

    def action_open_latest_einvoice_submission(self):
        raise_contact_message()

    def action_open_einvoice_submissions(self):
        return self.action_open_latest_einvoice_submission()

    def _send_invoice_to_api(self, move):
        move.action_orchida_send()
        return move.orchida_submission_state == 'valid'
