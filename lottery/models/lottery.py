# -*- coding: utf-8 -*-
from odoo import api
from odoo import fields
from odoo import models


class LotteryGameType(models.Model):
    _name = 'lottery.game.type'

    name = fields.Char(translate=True)
    active = fields.Boolean(default=True)


class LotteryGame(models.Model):
    _name = 'lottery.game'

    name = fields.Char()
    type_id = fields.Many2one('lottery.game.type', string='Game type', ondelete='restrict', required=True)
