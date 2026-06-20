from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char('Title', required=True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date(
        'Available from',
        copy=False,
        default=lambda self: fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float('Expected price', required=True)
    selling_price = fields.Float('Selling price', readonly=True, copy=False)
    bedrooms = fields.Integer('Bedrooms', default=2)
    living_area = fields.Integer('Living area (sqm)')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden area (sqm)')
    garden_orientation = fields.Selection(
        string='Garden orientation',
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ])
    state = fields.Selection(
        string='Status',
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer received'),
            ('offer_accepted', 'Offer accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        default='new',
        required=True,
        copy=False,
    )
    active = fields.Boolean('Active', default=True)
    property_type_id = fields.Many2one(
        'estate.property.type',
        string='Property type'
    )
    salesman_id = fields.Many2one(
        'res.users',
        string='Salesman',
        default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        copy=False
    )
    tag_ids = fields.Many2many(
        'estate.property.tag',
        string='Tags'
    )
    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_id',
        string='Offers'
    )
    total_area = fields.Float(
        string='Total area',
        compute='_compute_total_area'
    )
    best_price = fields.Float(
        string='Best offer',
        compute='_compute_best_price'
    )

    _sql_constraints = [
        (
            'check_expected_price', 'CHECK(expected_price > 0)',
            'The expected price must be strictly positive'
        ),
        (
            'check_selling_price', 'CHECK(selling_price >= 0)',
            'The selling price must be positive'
        )
    ]

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(
                record.offer_ids.mapped('price'),
                default=0
            )

    @api.constrains('selling_price', 'expected_price')
    def _check_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                return

            min_selling_price = record.expected_price * 0.90
            is_valid_selling_price = float_compare(
                record.selling_price, min_selling_price, precision_digits=2
            ) == -1
            if is_valid_selling_price:
                raise ValidationError(
                    'The selling price must be at least 90% of the expected '
                    'price! You must reduce the expected price if you want to '
                    'accept this offer.'
                )

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = False
            self.garden_orientation = False

    @api.ondelete(at_uninstall=False)
    def unlink_if_state_new_or_cancelled(self):
        if any(
            property.state not in ('new', 'cancelled')
            for property in self
        ):
            raise UserError(
                'Only new and cancelled properties can be deleted.'
            )

    def action_set_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError('Cancelled properties cannot be sold.')
            if record.state != 'offer_accepted':
                raise UserError('Accept an offer first before selling')
            record.state = 'sold'
            record.selling_price = record.best_price
        return True

    def action_set_cancelled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Sold properties cannot be cancelled.')
            record.state = 'cancelled'
        return True
