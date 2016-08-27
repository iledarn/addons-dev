# -*- coding: utf-8 -*-
from openerp import api
from openerp import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        if self.env.user.branch_id:
            res['domain']['journal_id'].append(('id',
                                                'in', (self.env.user.branch_id.cash_journal_id.id,
                                                       self.env.user.branch_id.bank_journal_id.id)))
        else:
            res['domain']['journal_id'].append(('id', 'not in',
                                                self.env['fleet_branch.branch'].search([]).mapped('cash_journal_id').ids +\
                                            self.env['fleet_branch.branch'].search([]).mapped('bank_journal_id').ids))
        return res