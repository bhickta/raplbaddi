# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class BrandSpecification(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.core.doctype.dynamic_link.dynamic_link import DynamicLink
		from frappe.types import DF
		from raplbaddi.raplbaddi.doctype.brand_alias.brand_alias import BrandAlias
		from raplbaddi.raplbaddi.doctype.sticker_item.sticker_item import StickerItem

		brand: DF.Link
		brand_aliases: DF.Table[BrandAlias]
		bypass_standard_stickers: DF.Check
		default_alias: DF.Data | None
		links: DF.Table[DynamicLink]
		stickers: DF.Table[StickerItem]
	# end: auto-generated types

	def autoname(self):
		self.name = self.brand

	@frappe.whitelist()
	def populate_alias(self):
		if not self.default_alias or self.brand_aliases:
			return
		geyser_models = frappe.get_all("Geyser Model", pluck="name")
		geyser_capacities = frappe.get_all("Geyser Capacity", pluck="name")
		for model, capacity in zip(geyser_models, geyser_capacities):
			self.append(
				"brand_aliases",
				{"model": model, "capacity": capacity, "alias": self.default_alias},
			)

	@frappe.whitelist()
	def populate_stickers(self):
		pass

	def validate(self):
		self.validate_name()
		self.validate_stickers()
	
	def validate_name(self):
		if self.name != self.brand:
			frappe.throw(_("Name must be same as brand"))

	def validate_stickers(self):
		if self.bypass_standard_stickers:
			return
		standard_stickers = [
			"Logo",
			"Lahar",
			"ISI",
			"Specification Plate",
			"Five Star",
			"Box Model Sticker",
		]
		sticker_type_set = set()
		for sticker in self.stickers:
			if sticker.sticker_type in sticker_type_set:
				frappe.throw(
					_("Duplicate sticker type found: {0}").format(sticker.sticker_type)
				)
			sticker_type_set.add(sticker.sticker_type)
		missing_stickers = set(standard_stickers) - sticker_type_set
		if missing_stickers:
			frappe.throw(
				_("Missing standard stickers: {0}").format(", ".join(missing_stickers))
			)
