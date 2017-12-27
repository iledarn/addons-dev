# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def _default_vehicle_id(self):
        invoice_id = self._context.get('default_invoice_id')
        if invoice_id:
            invoice = self.env['account.invoice'].browse(invoice_id)
            return invoice.vehicle_id.id

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', default=_default_vehicle_id)

    @api.multi
    @api.constrains('start_date', 'end_date')
    def _check_start_end_dates(self):
        super(AccountInvoiceLine, self)._check_start_end_dates()
        for invline in self:
            if invline.start_date and datetime.strptime(invline.start_date, DF).date() < datetime.now().date():
                raise ValidationError(
                    _("Start Date shouldn't be less than today for invoice line with "
                        "Description '%s'.")
                    % (invline.name))
            if invline.end_date and datetime.strptime(invline.end_date, DF).date() < datetime.now().date():
                raise ValidationError(
                    _("End Date shouldn't be less than today for invoice line with "
                        "Description '%s'.")
                    % (invline.name))