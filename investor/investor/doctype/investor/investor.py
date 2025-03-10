# Copyright (c) 2023, alaalsalam and contributors
# For license information, please see license.txt

import frappe
import frappe.defaults
from frappe import _, msgprint
from frappe.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact,
)
from frappe.model.naming import set_name_by_naming_series, set_name_from_naming_options

from erpnext.accounts.party import (  # noqa
	get_dashboard_info,
	validate_party_accounts,
)
from erpnext.utilities.transaction_base import TransactionBase


# import frappe
from frappe.model.document import Document

class Investor(TransactionBase):
	def get_feed(self):
		return self.investor_name

	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)
		# self.load_dashboard_info()  

	def before_save(self):
		if not self.on_hold:
			self.hold_type = ""
			self.release_date = ""
		elif self.on_hold and not self.hold_type:
			self.hold_type = "All"

	def load_dashboard_info(self):
		info = get_dashboard_info(self.doctype, self.name)
		self.set_onload("dashboard_info", info)

	def autoname(self):
		investor_master_name = frappe.defaults.get_global_default("investor_master_name")
		if investor_master_name == "Investor Name":
			self.name = self.investor_name
		elif investor_master_name == "Naming Series":
			set_name_by_naming_series(self)
		else:
			self.name = set_name_from_naming_options(frappe.get_meta(self.doctype).autoname, self)

	def on_update(self):
		if not self.naming_series:
			self.naming_series = ""

		self.create_primary_contact()
		self.create_primary_address()

	def validate(self):
		self.flags.is_new_doc = self.is_new()

		# validation for Naming Series mandatory field...
		if frappe.defaults.get_global_default("investor_master_name") == "Naming Series":
			if not self.naming_series:
				msgprint(_("Series is mandatory"), raise_exception=1)

		validate_party_accounts(self)
		# self.validate_internal_investor()

	@frappe.whitelist()
	def get_investor_group_details(self):
		doc = frappe.get_doc("Investor Group", self.investor_group)
		self.payment_terms = ""
		self.accounts = []

		if doc.accounts:
			for account in doc.accounts:
				child = self.append("accounts")
				child.company = account.company
				child.account = account.account

		if doc.payment_terms:
			self.payment_terms = doc.payment_terms

		self.save()

	# def validate_internal_investor(self):
	# 	if not self.is_internal_investor:
	# 		self.represents_company = ""

	# 	internal_investor = frappe.db.get_value(
	# 		"Investor",
	# 		{
	# 			"is_internal_investor": 1,
	# 			"represents_company": self.represents_company,
	# 			"name": ("!=", self.name),
	# 		},
	# 		"name",
	# 	)

	# 	if internal_investor:
	# 		frappe.throw(
	# 			_("Internal Investor for company {0} already exists").format(
	# 				frappe.bold(self.represents_company)
	# 			)
	# 		)

	def create_primary_contact(self):
		from erpnext.selling.doctype.customer.customer import make_contact

		if not self.investor_primary_contact:
			if self.mobile_no or self.email_id:
				contact = make_contact(self)
				self.db_set("investor_primary_contact", contact.name)
				self.db_set("mobile_no", self.mobile_no)
				self.db_set("email_id", self.email_id)

	def create_primary_address(self):
		from frappe.contacts.doctype.address.address import get_address_display

		from erpnext.selling.doctype.customer.customer import make_address

		if self.flags.is_new_doc and self.get("address_line1"):
			address = make_address(self)
			address_display = get_address_display(address.name)

			self.db_set("investor_primary_address", address.name)
			self.db_set("primary_address", address_display)

	def on_trash(self):
		if self.investor_primary_contact:
			frappe.db.sql(
				"""
				UPDATE `tabInvestor`
				SET
					investor_primary_contact=null,
					investor_primary_address=null,
					mobile_no=null,
					email_id=null,
					primary_address=null
				WHERE name=%(name)s""",
				{"name": self.name},
			)

		delete_contact_and_address("Investor", self.name)

	def after_rename(self, olddn, newdn, merge=False):
		if frappe.defaults.get_global_default("investor_master_name") == "Investor Name":
			self.db_set("investor_name", newdn)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_investor_primary_contact(doctype, txt, searchfield, start, page_len, filters):
	investor = filters.get("investor")
	return frappe.db.sql(
		"""
		SELECT
			`tabContact`.name from `tabContact`,
			`tabDynamic Link`
		WHERE
			`tabContact`.name = `tabDynamic Link`.parent
			and `tabDynamic Link`.link_name = %(investor)s
			and `tabDynamic Link`.link_doctype = 'Investor'
			and `tabContact`.name like %(txt)s
		""",
		{"investor": investor, "txt": "%%%s%%" % txt},
	)
 
