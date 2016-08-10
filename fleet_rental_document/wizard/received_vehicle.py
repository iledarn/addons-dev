# -*- coding: utf-8 -*-
from openerp import models, fields, api


class FleetRentalReceivedVehicleWizard(models.TransientModel):
    _name = "fleet_rental.received_vehicle_wizard"

    document_rent = fields.Many2one('fleet_rental.document_rent', string='Agreement Number',
                                       domain = lambda self: [('vehicle_id.branch_id', '=', self.env.user.branch_id.id), ('state', 'in', ['confirmed', 'extended'])])
    vehicle = fields.Many2one('fleet.vehicle', string='Car Plate',
                                domain = lambda self: [('branch_id', '=', self.env.user.branch_id.id), ('state_id', '=', self.env.ref('fleet.vehicle_state_booked').id)])

    @api.onchange('document_rent')
    def _onchange_document_rent(self):
        self.vehicle = self.document_rent.vehicle_id

    @api.onchange('vehicle')
    def _onchange_vehicle(self):
        if self.vehicle:
            self.document_rent = self.env['fleet_rental.document_rent'].search([('vehicle_id', '=', self.vehicle.id)], limit=1)

    @api.multi
    def action_receive(self):
        return self.document_rent.action_create_return()
