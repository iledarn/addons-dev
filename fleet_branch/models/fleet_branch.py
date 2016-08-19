# -*- coding: utf-8 -*-
from openerp import api, fields, models


class FleetBranch(models.Model):
    _name = "fleet_branch.branch"

    name = fields.Char('Branch Name', required=True)
    city = fields.Char(string='City')
    phone = fields.Char(string='Phone')
    branch_target = fields.Char(string='Branch Target')
    branch_officer_ids = fields.One2many('res.users', 'branch_id',
                                         string="Branch Officers", readonly=True)
    state = fields.Selection([('new', 'New'),
                              ('active', 'Active')],
                             string='State', default='new')

    deposit_account_id = fields.Many2one("account.account", string="Advanced Deposit Account",
                                         domain=[('deprecated', '=', False)],
                                         help="Account used for deposits", required=True)
    rental_account_id = fields.Many2one("account.account", string="Sales Account",
                                        domain=[('deprecated', '=', False)],
                                        help="Account used for rental sales", required=True)
    deposit_product_id = fields.Many2one('product.product', 'Deposit Product',
                                         domain="[('type', '=', 'service')]")
    rental_product_id = fields.Many2one('product.product', 'Rental Product',
                                        domain="[('type', '=', 'service')]")
