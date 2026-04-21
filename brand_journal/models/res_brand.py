# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResBrand(models.Model):
    _inherit = "res.brand"

    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Customer Invoice Journal",
        domain="['&', ('type', '=', 'sale'), '|', ('company_id', '=', False), ('company_id', 'in', allowed_company_ids)]",
        help="Sales journal to use for customer invoices created with this brand.",
    )
    purchase_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Vendor Bill Journal",
        domain="['&', ('type', '=', 'purchase'), '|', ('company_id', '=', False), ('company_id', 'in', allowed_company_ids)]",
        help="Purchase journal to use for vendor bills created with this brand.",
    )
