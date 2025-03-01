
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
	# @frappe.whitelist()
	# def validate(self):
	# 	pass
	# 	# self.calculate_total()
	# # 	self.set_missing_accounts_and_fields()

	# # def set_missing_accounts_and_fields(self):
	# 	if not self.company:
	# 		self.company = frappe.defaults.get_defaults().company
	# 	if not self.currency:
	# 		self.currency = erpnext.get_company_currency(self.company)
	# 	if not (self.custom_profit_and_loss_account_to_project):
	# 		accounts_details = frappe.get_all(
	# 			"Investor Settings",
	# 			fields=["default_profit_and_loss_account_to_project", "default_income_account", "cost_center"],
	# 			filters={"name": self.company},
	# 		)[0]
	# 	if not self.custom_profit_and_loss_account_to_project:
	# 		self.custom_profit_and_loss_account_to_project = accounts_details.default_profit_and_loss_account_to_project
	# 	# if not self.income_account:
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

	def update_billed_amount(self):

		# nosemgrep
		total_billed_amount = frappe.db.sql(
			"""select sum(base_net_amount)
			from `tabSales Invoice Item` si_item, `tabSales Invoice` si
			where si_item.parent = si.name
				and if(si_item.project, si_item.project, si.project) = %s
				and si.docstatus=1""",
			self.name,
		)

		self.total_billed_amount = total_billed_amount and total_billed_amount[0][0] or 0
		self.custom_project_amount = total_billed_amount and total_billed_amount[0][0] or 0
		self.calculate_sales_data()
	def update_purchase_costing(self):
		
		from erpnext.projects.doctype.project.project import calculate_total_purchase_cost

		total_purchase_cost = calculate_total_purchase_cost(self.name)
		self.total_purchase_cost = total_purchase_cost and total_purchase_cost[0][0] or 0
		self.custom_project_cost = total_purchase_cost and total_purchase_cost[0][0] or 0
	
	def calculate_sales_data(self):

		sales_invoices = frappe.get_all(
			"Sales Invoice",
			filters={"project": self.name, "docstatus": 1},
			fields=["name"]
		)
		
		total_cost = 0
		total_profit = 0

		for invoice in sales_invoices:
			items = frappe.get_all(
				"Sales Invoice Item",
				filters={"parent": invoice.name},
				fields=["item_code", "qty", "base_amount"]
			)

			for item in items:
				valuation_rate = frappe.db.get_value("Item", item["item_code"], "valuation_rate") or 0

				item_cost = item["qty"] * valuation_rate
				item_profit = item["base_amount"] - item_cost

				total_cost += item_cost
				total_profit += item_profit

		self.custom_total_cost_of_items_sold = total_cost
		self.custom_total_profit = total_profit
	
	