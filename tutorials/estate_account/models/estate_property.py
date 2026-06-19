from odoo import models


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_set_sold(self):
        for record in self:
            self.env['account.move'].create({
                'partner_id': record.buyer.id,
                'move_type': 'out_invoice'
            })
        return super().action_set_sold()
