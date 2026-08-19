from odoo import models, fields, _
from odoo.exceptions import UserError

from ..contact import raise_contact_message


class OrchidaPurchaseInvoice(models.Model):
    _name = 'orchida.purchase.invoice'
    _description = 'Orchida AP Invoices'
    _rec_name = 'invoice_number'

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )

    invoice_number = fields.Char(index=True)
    status = fields.Selection([
        ('pending', 'pending'),
        ('valid', 'valid'),
        ('invalid', 'invalid'),
    ], string="Tax Status", default='pending')
    raw_response = fields.Text()

    # extracted data
    issue_date = fields.Date()
    currency = fields.Char()
    supplier_name = fields.Char()
    total_amount = fields.Float()
    invoice_xml = fields.Text()
    vendor_bill_id = fields.Many2one('account.move', readonly=True, copy=False)
    import_error = fields.Text(readonly=True, copy=False)

    def action_view_pdf(self):
        return self.env.ref(
            'orchida_uae_e_invoicing_trial.report_orchida_invoice_pdf'
        ).report_action(self)

    def _decode_invoice(self, data):
        raise_contact_message()

    def _parse_xml(self, xml):
        raise_contact_message()

    def action_view_ubl_pdf(self):
        return self.env.ref(
            'orchida_uae_e_invoicing_trial.report_orchida_invoice_ubl_pdf'
        ).report_action(self)

    def _find_or_create_supplier(self, parsed):
        raise_contact_message()

    def _get_or_create_import_product(self, company, line_name):
        raise_contact_message()

    def _prepare_vendor_bill_line_vals(self, company, parsed_line):
        raise_contact_message()

    def _prepare_vendor_bill_vals(self, parsed):
        raise_contact_message()

    def _find_existing_vendor_bill(self, invoice_number):
        raise_contact_message()

    def _create_vendor_bill_from_orchida(self):
        raise_contact_message()

    def _parse_xml_ubl_pdf(self, xml):
        raise_contact_message()
