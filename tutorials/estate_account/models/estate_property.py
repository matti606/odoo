from odoo import models


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_set_sold(self):
        print('this should work, this is the link module')
        return super().action_set_sold()
