from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    name = fields.Char('Name', required=True)

    _sql_constraints = [
        (
            'name_unique', 'unique(name)',
            'The name must be unique'
        )
    ]
