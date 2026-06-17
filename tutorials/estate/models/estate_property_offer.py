from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

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

    _sql_constraints = [
        (
            'check_price', 'CHECK(price > 0)',
            'The offer price must be strictly positive'
        )
    ]

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

    def action_accept_offer(self):
        for record in self:
            if any(
                offer.status == 'accepted'
                for offer in record.property_id.offer_ids
            ):
                raise UserError('An offer is already accepted.')

            record.status = 'accepted'
            record.property_id.buyer = record.partner_id
            record.property_id.selling_price = record.price
        return True

    def action_refuse_offer(self):
        for record in self:
            record.status = 'refused'
            if not any(
                offer.status == 'accepted'
                for offer in record.property_id.offer_ids
            ):
                record.property_id.buyer = False
                record.property_id.selling_price = False
        return True
