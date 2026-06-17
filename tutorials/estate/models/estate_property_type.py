from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'name'

    name = fields.Char('Name', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')

    _sql_constraints = [
        (
            'name_unique', 'unique(name)',
            'The name must be unique'
        )
    ]
