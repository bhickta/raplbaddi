from erpnext.controllers.taxes_and_totals import (
    calculate_taxes_and_totals as base_calculate_taxes_and_totals,
    flt,
    frappe
)


class calculate_taxes_and_totals(base_calculate_taxes_and_totals):

    def _get_tax_rate(self, tax, item_tax_map):
        if self.doc.custom_tax_rate:
            return self.doc.custom_tax_rate
        if tax.account_head in item_tax_map:
            return flt(
                item_tax_map.get(tax.account_head), self.doc.precision("rate", tax)
            )
        else:
            return tax.rate

    def set_cumulative_total(self, row_idx, tax):
        tax_amount = tax.tax_amount_after_discount_amount
        tax_amount = self.get_tax_amount_if_for_valuation_or_deduction(tax_amount, tax)

        if self.doc.get("custom_grand_total") and self.doc.get("custom_tax_rate"):
            tax.total = flt(
                self.doc.custom_grand_total + tax_amount, tax.precision("total")
            )
            tax.rate = flt(self.doc.custom_tax_rate, tax.precision("rate"))
        elif row_idx == 0:
            tax.total = flt(self.doc.net_total + tax_amount, tax.precision("total"))
        else:
            tax.total = flt(
                self.doc.get("taxes")[row_idx - 1].total + tax_amount,
                tax.precision("total"),
            )

    def round_off_totals(self, tax):
        if tax.account_head in frappe.flags.round_off_applicable_accounts:
            tax.tax_amount = round(tax.tax_amount, 0)
            tax.tax_amount_after_discount_amount = round(
                tax.tax_amount_after_discount_amount, 0
            )

        tax.tax_amount = flt(tax.tax_amount, tax.precision("tax_amount"))
        tax.tax_amount_after_discount_amount = flt(
            tax.tax_amount_after_discount_amount, tax.precision("tax_amount")
        )
        print(tax.rate, self.doc.custom_grand_total, self.doc.custom_tax_rate)
        if self.doc.get("custom_grand_total") and self.doc.get("custom_tax_rate"):
            tax.tax_amount = self.doc.custom_grand_total * tax.rate * 0.01
            tax.tax_amount_after_discount_amount = tax.tax_amount


    def calculate_totals(self):
        if self.doc.get("taxes"):
            self.doc.grand_total = flt(self.doc.get("taxes")[-1].total) + flt(
                self.doc.get("grand_total_diff")
            )
        else:
            self.doc.grand_total = flt(self.doc.net_total)

        if self.doc.get("taxes"):
            if self.doc.custom_grand_total:
                self.doc.total_taxes_and_charges = flt(
                    self.doc.grand_total
                    - self.doc.custom_grand_total
                    - flt(self.doc.get("grand_total_diff")),
                    self.doc.precision("total_taxes_and_charges"),
                )
            else:
                self.doc.total_taxes_and_charges = flt(
                    self.doc.grand_total
                    - self.doc.net_total
                    - flt(self.doc.get("grand_total_diff")),
                    self.doc.precision("total_taxes_and_charges"),
                )
        else:
            self.doc.total_taxes_and_charges = 0.0

        self._set_in_company_currency(
            self.doc, ["total_taxes_and_charges", "rounding_adjustment"]
        )

        if self.doc.doctype in [
            "Quotation",
            "Sales Order",
            "Delivery Note",
            "Sales Invoice",
            "POS Invoice",
        ]:
            self.doc.base_grand_total = (
                flt(
                    self.doc.grand_total * self.doc.conversion_rate,
                    self.doc.precision("base_grand_total"),
                )
                if self.doc.total_taxes_and_charges
                else self.doc.base_net_total
            )
        else:
            self.doc.taxes_and_charges_added = self.doc.taxes_and_charges_deducted = 0.0
            for tax in self.doc.get("taxes"):
                if tax.category in ["Valuation and Total", "Total"]:
                    if tax.add_deduct_tax == "Add":
                        self.doc.taxes_and_charges_added += flt(
                            tax.tax_amount_after_discount_amount
                        )
                    else:
                        self.doc.taxes_and_charges_deducted += flt(
                            tax.tax_amount_after_discount_amount
                        )

            self.doc.round_floats_in(
                self.doc, ["taxes_and_charges_added", "taxes_and_charges_deducted"]
            )

            self.doc.base_grand_total = (
                flt(self.doc.grand_total * self.doc.conversion_rate)
                if (
                    self.doc.taxes_and_charges_added
                    or self.doc.taxes_and_charges_deducted
                )
                else self.doc.base_net_total
            )

            self._set_in_company_currency(
                self.doc, ["taxes_and_charges_added", "taxes_and_charges_deducted"]
            )

        self.doc.round_floats_in(self.doc, ["grand_total", "base_grand_total"])

        self.set_rounded_total()