# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import openerp.addons.decimal_precision as dp


class FleetRentalDocumentExtend(models.Model):
    _name = 'fleet_rental.document_extend'
    _inherits = {'fleet_rental.document_rent': 'document_rent_id',
                 'fleet_rental.document': 'document_id'}

    document_id = fields.Many2one('fleet_rental.document', required=True,
                                  ondelete='restrict', auto_join=True)
    document_rent_id = fields.Many2one('fleet_rental.document_rent',
                                       ondelete='restrict', auto_join=True, required=True)

    name = fields.Char(string='Agreement Number', required=True,
                       copy=False, readonly=True, index=True, default='New')
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 domain=[('customer', '=', True)], required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('extended', 'Extended'),
        ('returned', 'Returned'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')
    type = fields.Selection([
        ('rent', 'Rent'),
        ('extend', 'Extend'),
        ('return', 'Return'),
        ], readonly=True, index=True, change_default=True)
    origin = fields.Char(string='Source Document',
                         help="Reference of the document that produced this document.",
                         readonly=True, states={'draft': [('readonly', False)]})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet_rental.document_extend') or 'New'
        result = super(FleetRentalDocumentExtend, self).create(vals)
        return result

    @api.multi
    def action_view_invoice(self):
        return self.mapped('document_id').action_view_invoice()
