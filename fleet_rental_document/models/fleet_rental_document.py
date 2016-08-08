# -*- coding: utf-8 -*-

import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp
import base64
from lxml import etree
import os
from wand.image import Image
from openerp.exceptions import AccessError, UserError


class FleetRentalDocument(models.Model):
    _name = 'fleet_rental.document'

    name = fields.Char(string='Agreement Number', required=True, copy=False, readonly=True, index=True, default='New')

    type = fields.Selection([
            ('rent','Rent'),
            ('extended_rent','Extended Rent'),
            ('return','Return'),
        ], readonly=True, index=True, change_default=True)

    origin = fields.Char(string='Source Document',
        help="Reference of the document that produced this document.",
        readonly=True, states={'draft': [('readonly', False)]})

    partner_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)], required=True)
    membership_type_id = fields.Many2one('sale_membership.type', related='partner_id.type_id', string='Membership')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)
    vehicle_color_id = fields.Many2one('fleet.vehicle_color', related='vehicle_id.color_id', readonly=True)
    license_plate = fields.Char('License Plate', related='vehicle_id.license_plate')
    account_move_ids = fields.One2many('account.move', 'fleet_rental_document_id', string='Entries', readonly=True)
    account_move_lines_ids = fields.One2many('account.move.line', 'fleet_rental_document_id', string='Entrie lines', readonly=True)
    allowed_kilometer_per_day = fields.Integer(string='Allowed kilometer per day')
    rate_per_extra_km = fields.Float(string='Rate per extra km')
    daily_rental_price = fields.Float(string='Daily Rental Price')
    odometer_before = fields.Float(string='Odometer', readonly=True, store=True)

    extra_driver_charge_per_day = fields.Float(string='Extra Driver Charge per day', digits_compute=dp.get_precision('Product Price'), default=0)
    other_extra_charges = fields.Float(string='Other Extra Charges', digits_compute=dp.get_precision('Product Price'), default=0)

    exit_datetime = fields.Datetime(string='Exit Date and Time')
    return_datetime = fields.Datetime(string='Return Date and Time')
    extend_return_datetime = fields.Datetime(string='Last extend return time', help='Last extend document return Date and Time', default=False, readonly=True)
    rent_return_datetime = fields.Datetime(string='Rent Return Date and Time')

    total_rental_period = fields.Integer(string='Total Rental Period', compute="_compute_total_rental_period", store=True, readonly=True)
    total_rent_price = fields.Float(string='Total Rent Price', compute="_compute_total_rent_price", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)

    period_rent_price = fields.Float(string='Period Rent Price', compute="_compute_period_rent_price", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)
    extra_driver_charge = fields.Float(string='Extra Driver Charge', compute="_compute_extra_driver_charge", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)
    advanced_deposit = fields.Float(string='Advanced Deposit', store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)
    balance = fields.Float(string='Balance', compute="_compute_balance", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True,
                           help='If balance is negative means we have to return amount to customer. If balance is positive means customer should to pay')

    check_line_ids = fields.Many2many('fleet_rental.check_line', string='Vehicle rental check lines')
    part_line_ids = fields.Many2many('fleet_rental.svg_vehicle_part_line', string='Vehicle part')

    invoice_ids = fields.Many2many("account.invoice", string='Invoices', compute="_get_invoiced", readonly=True, copy=False)
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced', readonly=True)
    invoice_line_ids = fields.One2many('account.invoice.line', 'fleet_rental_document_id', string='Invoice Lines', copy=False)

    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)

    png_file = fields.Text('PNG', compute='_compute_png', store=False)

    @api.one
    @api.constrains('total_rental_period')
    def _check_return_date(self):
        if self.total_rental_period < 1:
            raise UserError('Return date cannot be set before or the same as Exit Date.')

    @api.one
    @api.constrains('partner_id')
    def _check_partner(self):
        if self.partner_id.blocked == True:
            reason = self.env['sale_membership.log'].search([('partner_id', '=', self.partner_id.id),
                                                            ('blocked', '=', True)],
                                                           order='create_date desc',
                                                           limit=1).reason
            raise UserError('The customer %s is blocked for this reason: %s.' % (self.partner_id.name, reason))

    @api.multi
    def _compute_png(self):
        for rec in self:
            f = open('/'.join([os.path.dirname(os.path.realpath(__file__)),
                               '../static/src/img/car-cutout.svg']), 'r')
            svg_file = f.read()
            dom = etree.fromstring(svg_file)
            for line in rec.part_line_ids:
                if line.state == 'broken':
                    for el in dom.xpath('//*[@id="%s"]' % line.part_id.path_ID):
                        el.attrib['fill'] = 'red'
            f.close()
            with Image(blob=etree.tostring(dom), format='svg') as img:
                rec.png_file = base64.b64encode(img.make_blob('png'))

    @api.multi
    def action_view_invoice(self):
        invoice_ids = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1')
        list_view_id = self.env.ref('account.invoice_tree').id
        form_view_id = self.env.ref('account.invoice_form').id

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % invoice_ids.ids
        elif len(invoice_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = invoice_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.depends('invoice_line_ids')
    def _get_invoiced(self):

        for document in self:
            invoice_ids = document.invoice_line_ids.mapped('invoice_id')
            # Search for refunds as well
            refund_ids = self.env['account.invoice'].browse()
            if invoice_ids:
                refund_ids = refund_ids.search([('type', '=', 'out_refund'), ('origin', 'in', invoice_ids.mapped('number')), ('origin', '!=', False)])

            document.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids,
            })

    @api.multi
    @api.depends('exit_datetime', 'return_datetime')
    def _compute_total_rental_period(self):
        for record in self:
            if record.exit_datetime and record.return_datetime:
                start = datetime.strptime(record.exit_datetime.split()[0], DEFAULT_SERVER_DATE_FORMAT)
                end = datetime.strptime(record.return_datetime.split()[0], DEFAULT_SERVER_DATE_FORMAT)
                record.total_rental_period = (end - start).days

    @api.multi
    @api.depends('daily_rental_price', 'total_rental_period')
    def _compute_period_rent_price(self):
        for record in self:
            record.period_rent_price = record.total_rental_period * record.daily_rental_price

    @api.depends('total_rental_period', 'extra_driver_charge_per_day')
    def _compute_extra_driver_charge(self):
        for record in self:
            if record.total_rental_period:
                record.extra_driver_charge = record.total_rental_period * record.extra_driver_charge_per_day

    @api.depends('period_rent_price', 'extra_driver_charge', 'other_extra_charges')
    def _compute_total_rent_price(self):
        for record in self:
            record.total_rent_price = record.period_rent_price + record.extra_driver_charge + record.other_extra_charges

    @api.multi
    @api.depends('partner_id.rental_deposit_analytic_account_id.line_ids.amount')
    def _compute_advanced_deposit(self):
        for record in self:
            account_analytic = record.partner_id.rental_deposit_analytic_account_id
            if account_analytic:
                account_analytic._compute_debit_credit_balance()
            record.advanced_deposit = account_analytic and account_analytic.balance or 0.0

    @api.depends('total_rent_price', 'advanced_deposit')
    def _compute_balance(self):
        for record in self:
            record.balance = record.total_rent_price - record.advanced_deposit


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    fleet_rental_document_id = fields.Many2one('fleet_rental.document', readonly=True, copy=False)

