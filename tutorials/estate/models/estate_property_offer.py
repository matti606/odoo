from datetime import timedelta
from odoo import models, fields, api


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float('Price')
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        copy=False
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True
    )
    property_id = fields.Many2one(
        'estate.property',
        string='Property',
        required=True
    )
    validity = fields.Integer('Validity (days)', default=7)
    date_deadline = fields.Date(
        'Deadline',
        compute='_compute_date_deadline',
        inverse='_inverse_date_deadline'
    )

    @api.depends('validity', 'create_date')
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = (
                record.create_date or fields.Date.today()
                ) + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (
                record.date_deadline - (
                    record.create_date.date() or fields.Date.today()
                )
            ).days
