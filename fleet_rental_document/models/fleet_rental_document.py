# -*- coding: utf-8 -*-
from openerp import models, fields, api


class FleetRentalDocument(models.Model):
    _name = 'fleet_rental.document'

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
        ('open', 'Open'),
        ('closed', 'Closed'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')
    type = fields.Selection([
        ('rent', 'Rent'),
        ('extend', 'Extend'),
        ('return', 'Return'),
        ], readonly=True, index=True, change_default=True)
    origin = fields.Char(string='Source Document',
                         help="Reference of the document that produced this document.",
                         readonly=True, states={'draft': [('readonly', False)]})
    invoice_ids = fields.Many2many("account.invoice", string='Invoices',
                                   compute="_get_invoiced", readonly=True, copy=False)
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced', readonly=True)
    invoice_line_ids = fields.One2many('account.invoice.line', 'fleet_rental_document_id',
                                       string='Invoice Lines', copy=False)
    rental_account_id = fields.Many2one('account.analytic.account',
                                        string='analytic account for rental', readonly=True)

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
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'],
                      [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
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
                refund_ids = refund_ids.search([('type', '=', 'out_refund'),
                                                ('origin', 'in', invoice_ids.mapped('number')),
                                                ('origin', '!=', False)])

            document.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids,
            })

    @api.multi
    def action_create_refund(self):
        pass
