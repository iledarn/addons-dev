# -*- coding: utf-8 -*-
from openerp import api, fields, models


class FleetBranch(models.Model):
    _name = "fleet_branch.branch"

    name = fields.Char('Branch Name', required=True)
    city = fields.Char(string='City')
    phone = fields.Char(string='Phone')
    branch_target = fields.Char(string='Branch Target')
    branch_officer_ids = fields.One2many('res.users', 'branch_id', readonly=True)
    state = fields.Selection([('new', 'New'),
                              ('active', 'Active')],
                             string='State', default='new')

