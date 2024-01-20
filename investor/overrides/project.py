
import frappe
import erpnext
from frappe import _
from frappe.utils import money_in_words
from erpnext.accounts.doctype.payment_request.payment_request import \
    make_payment_request
from frappe.utils.csvutils import getlink
from erpnext.accounts.general_ledger import make_reverse_gl_entries

from erpnext.projects.doctype.project.project import Project

class ProjectCustom(Project):
	@frappe.whitelist()
	def validate(self):
		pass
		# self.calculate_total()
	# 	self.set_missing_accounts_and_fields()

	# def set_missing_accounts_and_fields(self):
		if not self.company:
			self.company = frappe.defaults.get_defaults().company
		if not self.currency:
			self.currency = erpnext.get_company_currency(self.company)
		if not (self.custom_profit_and_loss_account_to_project):
			accounts_details = frappe.get_all(
				"Investor Settings",
				fields=["default_profit_and_loss_account_to_project", "default_income_account", "cost_center"],
				filters={"name": self.company},
			)[0]
		if not self.custom_profit_and_loss_account_to_project:
			self.custom_profit_and_loss_account_to_project = accounts_details.default_profit_and_loss_account_to_project
		# if not self.income_account:
		# 	self.income_account = accounts_details.default_income_account
		# if not self.cost_center:
		# 	self.cost_center = accounts_details.cost_center
		
	# def on_submit(self):
	# 	self.make_gl_entries()


	# def on_cancel(self):
	# 	self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
	# 	make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
	# 	# frappe.db.set(self, 'status', 'Cancelled')

	# def make_gl_entries(self):
	# 	if not self.gross_margin:
	# 		return
	# 	investor_gl_entries = self.get_gl_dict(
	# 		{
	# 			"account": self.custom_profit_and_loss_account_to_project,
	# 			"party_type": "Investor",
	# 			"party": self.student,
	# 			"against": self.income_account,
	# 			"debit": self.gross_margin,
	# 			"debit_in_account_currency": self.gross_margin,
	# 			"against_voucher": self.name,
	# 			"against_voucher_type": self.doctype,
	# 		},
	# 		item=self,
	# 	)

	# 	fee_gl_entry = self.get_gl_dict(
	# 		{
	# 			"account": self.income_account,
	# 			"against": self.student,
	# 			"credit": self.grand_total,
	# 			"credit_in_account_currency": self.grand_total,
	# 			"cost_center": self.cost_center,
	# 		},
	# 		item=self,
	# 	)

	# 	from erpnext.accounts.general_ledger import make_gl_entries

	# 	make_gl_entries(
	# 		[investor_gl_entries, fee_gl_entry],
	# 		cancel=(self.docstatus == 2),
	# 		update_outstanding="Yes",
	# 		merge_entries=False,
	# 	)

