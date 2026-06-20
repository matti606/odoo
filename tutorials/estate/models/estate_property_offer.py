from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


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
    property_type_id = fields.Many2one(related='property_id.property_type_id')

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            estate_property = self.env['estate.property'].browse(
                vals['property_id']
            )

            if estate_property.offer_ids:
                highest_offer = max(estate_property.offer_ids.mapped('price'))
                offer_too_low = float_compare(
                    vals['price'], highest_offer, precision_digits=2
                ) == -1
                if offer_too_low:
                    raise UserError(
                        'The offer must be higher than %.2f' % highest_offer
                    )

            estate_property.state = 'offer_received'
        return super().create(vals_list)

    def action_accept_offer(self):
        for record in self:
            if any(
                offer.status == 'accepted'
                for offer in record.property_id.offer_ids
            ):
                raise UserError('An offer is already accepted.')

            record.status = 'accepted'
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = 'offer_accepted'
        return True

    def action_refuse_offer(self):
        for record in self:
            record.status = 'refused'
            if not any(
                offer.status == 'accepted'
                for offer in record.property_id.offer_ids
            ):
                record.property_id.buyer_id = False
                record.property_id.selling_price = False
                record.property_id.state = 'offer_received'
        return True
