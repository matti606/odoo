from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char('Title', required=True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date(
        'Available from',
        copy=False,
        default=fields.Date.today() + relativedelta(months=3))
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
    salesman = fields.Many2one(
        'res.users',
        string='Salesman',
        default=lambda self: self.env.user
    )
    buyer = fields.Many2one(
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
