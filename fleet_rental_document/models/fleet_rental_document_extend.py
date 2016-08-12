# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import openerp.addons.decimal_precision as dp


class FleetRentalDocumentExtend(models.Model):
    _name = 'fleet_rental.document_extend'
    _inherits = {
                 'fleet_rental.document_rent': 'document_rent_id',
                 }
    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')

    document_rent_id = fields.Many2one('fleet_rental.document_rent')
