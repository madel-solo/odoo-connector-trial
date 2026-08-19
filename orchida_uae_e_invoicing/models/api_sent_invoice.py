import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from ..contact import raise_contact_message


class ApiSentInvoice(models.Model):
    _name = "api.sent.invoice"
    _description = "E-Invoice Submissions"
    _order = "sent_date desc"

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    move_id = fields.Many2one("account.move", string="Invoice", required=True)
    move_name = fields.Char(string="Invoice Number", related="move_id.name", store=True)
    partner_id = fields.Many2one(related="move_id.partner_id", string="Customer", store=True)
    amount_total = fields.Monetary(related="move_id.amount_total", string="Total", store=True)
    currency_id = fields.Many2one(related="move_id.currency_id", string="Currency", store=True)
    sent_date = fields.Datetime(default=fields.Datetime.now, string="Sent Date")
    last_sync = fields.Datetime(default=fields.Datetime.now, string="Last Sync")
    success = fields.Boolean(string="Success")
    move_type = fields.Selection(related="move_id.move_type", string="Type", store=True)
    outcome = fields.Selection(
        [
            ('valid', 'Valid'),
            ('failed', 'Action Required'),
            ('unknown', 'Processing'),
        ],
        default='failed',
        required=True,
        index=True,
    )
    source = fields.Selection(
        [
            ('automatic', 'Automatic'),
            ('manual', 'Manual'),
            ('retry', 'Retry'),
            ('legacy', 'Legacy'),
        ],
        default='legacy',
        required=True,
    )
    internal_code = fields.Char(string='Internal Code', index=True)
    request_payload = fields.Text(
        string='Request Payload',
        groups='account.group_account_user',
    )
    status_response = fields.Text(string='Status Response')
    http_status = fields.Integer(string='HTTP Status')
    attempt_count = fields.Integer(string='HTTP Attempts', default=1)
    api_uuid = fields.Char(string='API UUID')
    failure_type = fields.Selection(
        [
            ('document', 'Document'),
            ('configuration', 'Configuration'),
            ('technical', 'Technical'),
        ],
        string='Failure Type',
    )

    taxAuthStatus = fields.Selection([
        ('pending', 'Pending'),
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
    ], string="Tax Status (legacy)", default='pending')

    receiverStatus = fields.Selection([
        ('pending', 'Pending'),
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('submitted', 'Submitted'),
    ], string="Receiver Status (legacy)", default='pending')

    orchida_tax_status = fields.Char(string="Tax Status", default='pending')
    orchida_receiver_status = fields.Char(string="Receiver Status", default='pending')
    response = fields.Text(string="API Response")
    response_short = fields.Char(string="Error Summary", compute="_compute_response_short", store=False)
    overall_status = fields.Char(string="Status", compute="_compute_overall_status", store=False)

    @api.depends('response', 'status_response')
    def _compute_response_short(self):
        for record in self:
            response = record.response or record.status_response
            if not response:
                record.response_short = ""
                continue
            try:
                data = json.loads(response)
                errors = data.get("errors", [])
                if errors:
                    msgs = [e.get("message", "") for e in errors if e.get("message")]
                    record.response_short = " | ".join(msgs)[:200]
                elif data.get("status") == "invalid":
                    record.response_short = (data.get("message") or "Invalid")[:200]
                else:
                    record.response_short = ""
            except Exception:
                record.response_short = response[:200]

    @api.depends('outcome', 'orchida_tax_status', 'orchida_receiver_status')
    def _compute_overall_status(self):
        for record in self:
            if record.outcome == 'valid':
                record.overall_status = 'valid'
                continue
            if record.outcome == 'unknown':
                record.overall_status = 'unknown'
                continue
            tax = (record.orchida_tax_status or '').lower()
            rec = (record.orchida_receiver_status or '').lower()
            if 'invalid' in tax or 'invalid' in rec or 'reject' in tax or 'reject' in rec or 'error' in tax or 'error' in rec:
                record.overall_status = 'invalid'
            elif tax == 'valid' and rec == 'valid':
                record.overall_status = 'valid'
            elif tax == 'pending' and rec == 'pending':
                record.overall_status = 'pending'
            else:
                record.overall_status = 'partial'

    def resend_invoice_to_api(self):
        raise_contact_message()

    def resend_invoice_form_to_api(self):
        raise_contact_message()

    def action_open_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': self.move_id.id,
        }

    def action_view_technical_details(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Technical Details'),
            'res_model': 'api.sent.invoice',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'orchida_uae_e_invoicing.view_api_sent_invoice_technical_form'
            ).id,
            'res_id': self.id,
            'target': 'new',
        }

    def action_open_submission_history(self):
        self.ensure_one()
        action = self.env.ref('orchida_uae_e_invoicing.action_api_sent_invoice').read()[0]
        action['domain'] = [('move_id', '=', self.move_id.id)]
        action['context'] = {'search_default_move_id': self.move_id.id}
        return action

    def action_retry_submission(self):
        raise_contact_message()

    def action_check_status(self):
        raise_contact_message()

    def action_correct_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Correction required'),
                'message': _(
                    'Fix the invoice data, save it, then click Submit E-Invoice.'
                ),
                'type': 'warning',
                'sticky': False,
                'next': self.action_open_invoice(),
            },
        }

    def _refresh_status_from_api(self):
        self.ensure_one()
        raise_contact_message()

    def get_ar_inv_id_status(self):
        raise_contact_message()

    def _cron_refresh_pending_status(self):
        return True
