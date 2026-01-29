# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResBrand(models.Model):
    _inherit = "res.brand"

    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Invoice Journal",
        domain="['&', ('type', '=', 'sale'), '|', ('company_id', '=', False), ('company_id', 'in', allowed_company_ids)]",
        help="Journal to use for invoices created with this brand.",
    )
