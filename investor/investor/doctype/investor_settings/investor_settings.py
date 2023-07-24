# Copyright (c) 2023, alaalsalam and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class InvestorSettings(Document):
	def validate(self):
		for key in ["investor_group", "investor_master_name","investor_currency"]:
			frappe.db.set_default(key, self.get(key, ""))

		from erpnext.utilities.naming import set_by_naming_series

		set_by_naming_series(
			"Investor",
			"investor_name",
			self.get("investor_master_name") == "Naming Series",
			hide_name_field=False,
		)

	def before_save(self):
		self.check_maintain_same_rate()

	def check_maintain_same_rate(self):
		if self.maintain_same_rate:
			self.set_landed_cost_based_on_purchase_invoice_rate = 0
