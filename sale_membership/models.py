# -*- coding: utf-8 -*-

from openerp import fields, models, api


class MemberType(models.Model):
    _name = 'sale_membership.type'
    _order = 'points'

    name = fields.Char('Membership type')
    points = fields.Integer('Promote at', default=0)


class MemberLog(models.Model):

    _name = 'sale_membership.log'

    partner_id = fields.Many2one('res.partner', string='Partner')
    member_type_id = fields.Many2one('sale_membership.type', string='New Membership Type')
    reason = fields.Char(string='Reason', help='Reason of membership change. But if blocked=True then reason of blocking')
    blocked = fields.Boolean('Blocked', default='False')


class Person(models.Model):

    _inherit = 'res.partner'

    points = fields.Float(string='Current membership Points', default=0, readonly=True)
    type_id = fields.Many2one('sale_membership.type', compute='set_membership', string='Current Membership type', store=True, readonly=True)
    blocked = fields.Boolean(default=False, string='Blocked', readonly=True)

    @api.one
    @api.depends('points', 'customer')
    def set_membership(self):
        if not self.customer:
            return
        l1 = self.env['sale_membership.type'].search([]).mapped('points')
        l2 = [x for x in l1 if self.points >= x]
        if l2:
            m = max(l2)
            self.type_id = self.env['sale_membership.type'].search([('points', '=', m)]).id
