# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    _BRAND_SALE_JOURNAL_MOVE_TYPES = (
        "out_invoice",
        "out_refund",
        "out_receipt",
    )
    _BRAND_PURCHASE_JOURNAL_MOVE_TYPES = (
        "in_invoice",
        "in_refund",
        "in_receipt",
    )
    _BRAND_JOURNAL_MOVE_TYPES = (
        *_BRAND_SALE_JOURNAL_MOVE_TYPES,
        *_BRAND_PURCHASE_JOURNAL_MOVE_TYPES,
    )

    @api.model
    def _brand_journal_from_brand(self, brand, move_type):
        if not brand:
            return False
        if move_type in self._BRAND_SALE_JOURNAL_MOVE_TYPES:
            return brand.journal_id
        if move_type in self._BRAND_PURCHASE_JOURNAL_MOVE_TYPES:
            return brand.purchase_journal_id
        return False

    @api.model
    def _brand_journal_from_vals(self, vals, move_type):
        brand_id = vals.get("brand_id")
        if not brand_id:
            return False
        brand = self.env["res.brand"].browse(brand_id)
        return self._brand_journal_from_brand(brand, move_type)

    def _default_journal_for_move(self):
        journal_model = self.env["account.journal"]
        move_type = self.move_type or self.env.context.get("default_move_type")
        company_id = self.company_id.id if self.company_id else False
        ctx = dict(self.env.context)
        if move_type:
            ctx["default_move_type"] = move_type
        if company_id:
            ctx["default_company_id"] = company_id
        defaults = self.with_context(ctx).default_get(["journal_id"])
        journal_id = defaults.get("journal_id")
        return journal_model.browse(journal_id) if journal_id else False

    def _apply_brand_journal(self, reset_if_no_brand=False):
        self.ensure_one()
        if self.move_type not in self._BRAND_JOURNAL_MOVE_TYPES:
            return
        if self.brand_id:
            journal = self._brand_journal_from_brand(self.brand_id, self.move_type)
            if journal:
                self.journal_id = journal
            return
        if reset_if_no_brand:
            default_journal = self._default_journal_for_move()
            if default_journal:
                self.journal_id = default_journal

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            move_type = vals.get("move_type") or self.env.context.get(
                "default_move_type"
            )
            if move_type not in self._BRAND_JOURNAL_MOVE_TYPES:
                continue
            journal = self._brand_journal_from_vals(vals, move_type)
            if journal:
                vals["journal_id"] = journal.id
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if "brand_id" in vals:
            for move in self.filtered(
                lambda m: m.state == "draft"
                and m.move_type in self._BRAND_JOURNAL_MOVE_TYPES
            ):
                move._apply_brand_journal(reset_if_no_brand=True)
        return res

    @api.onchange("brand_id", "company_id", "move_type")
    def _onchange_brand_id(self):
        res = super()._onchange_brand_id()
        for move in self:
            move._apply_brand_journal(reset_if_no_brand=True)
        return res
