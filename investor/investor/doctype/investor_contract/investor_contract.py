# Copyright (c) 2023, alaalsalam and contributors
# For license information, please see license.txt

import frappe
import erpnext

from frappe import _
from erpnext.controllers.accounts_controller import AccountsController
# from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from frappe.utils import money_in_words
from erpnext.accounts.doctype.payment_request.payment_request import \
    make_payment_request
from frappe.utils.csvutils import getlink
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.accounts.general_ledger import make_reverse_gl_entries

from frappe.utils import (
	flt,
 )

class investorContract(AccountsController):
	def autoname(self):
		name = self.party_name
		if self.contract_template:
			name += " - {}".format(self.contract_template)
		# If identical, append contract name with the next number in the iteration
		if frappe.db.exists("Contract", name):
			count = len(frappe.get_all("Contract", filters={"name": ["like", "%{}%".format(name)]}))
			name = "{} - {}".format(name, count)

		self.name = _(name)

	# def on_cancel(self):
	# 	self.ignore_linked_doctypes = ("GL Entry")
	# 	if self.profit_and_loss_account_to_project:
	# 		self.make_gl_entries()
	def on_update_after_submit(self):
		self.on_update()
		# self.make_gl_entries()
  
	def on_update(self):
		self.update_profit()
     
    
    
		if self.investment_percent:
			self.investment_profit= ( self.project_profit * self.investment_percent) / 100
			self.investment_profit_per = ( self.investment_profit * 100) / self.investment_amount
		#
		# self.make_gl_entries()

		# if self.profit_and_loss_account_to_project:
		# 	balanc = get_account_balance(account = self.profit_and_loss_account_to_project, project = self.project)
		# 	if balanc < 1:
		# 		balanc = balanc * -1
		# 	self.project_profit = balanc			
		
	def validate(self):
		
		self.validate_dates()
		self.update_contract_status()
		self.update_fulfilment_status()

	def before_submit(self):
		self.signed_by_company = frappe.session.user

	def before_update_after_submit(self):
		self.update_contract_status()
		self.update_fulfilment_status()

	def validate_dates(self):
		if self.end_date and self.end_date < self.start_date:
			frappe.throw(_("End Date cannot be before Start Date."))

	def update_contract_status(self):
		if self.is_signed:
			self.status = get_status(self.start_date, self.end_date)
		else:
			self.status = "Unsigned"

	def update_fulfilment_status(self):
		fulfilment_status = "N/A"

		if self.requires_fulfilment:
			fulfilment_progress = self.get_fulfilment_progress()

			if not fulfilment_progress:
				fulfilment_status = "Unfulfilled"
			elif fulfilment_progress < len(self.fulfilment_terms):
				fulfilment_status = "Partially Fulfilled"
			elif fulfilment_progress == len(self.fulfilment_terms):
				fulfilment_status = "Fulfilled"

			if fulfilment_status != "Fulfilled" and self.fulfilment_deadline:
				now_date = getdate(nowdate())
				deadline_date = getdate(self.fulfilment_deadline)

				if now_date > deadline_date:
					fulfilment_status = "Lapsed"

		self.fulfilment_status = fulfilment_status

	def get_fulfilment_progress(self):
		return len([term for term in self.fulfilment_terms if term.fulfilled])

	def update_profit(self):  
		if self.investment_profit:
			for divied in self.contract_dividend_ratios:
				divied.profit_amount = (self.investment_profit * divied.dividend) / 100
        
	def set_indicator(self):
		"""Set indicator for portal"""
		if self.investment_profit > 20000:
			self.indicator_color = "orange"
			self.indicator_title = _("Unpaid")
		else:
			self.indicator_color = "green"
			self.indicator_title = _("Paid")

	def validate(self):
     
		self.calculate_total_delate()
		# self.set_missing_accounts_and_fields()

	def set_missing_accounts_and_fields(self):
		if not self.company:
			self.company = frappe.defaults.get_defaults().company
		if not self.currency:
			self.currency = erpnext.get_company_currency(self.company)
		if not (self.receivable_account and self.income_account and self.cost_center):
			accounts_details = frappe.get_all(
				"Company",
				fields=["default_receivable_account", "default_income_account", "cost_center"],
				filters={"name": self.company},
			)[0]
		# if not self.receivable_account:
		# 	self.receivable_account = accounts_details.default_receivable_account
		# if not self.income_account:
		# 	self.income_account = accounts_details.default_income_account
		# if not self.cost_center:
		# 	self.cost_center = accounts_details.cost_center

	

	def calculate_total_delate(self):
		"""Calculates total amount."""
		self.investment_amount_in_words = money_in_words(self.investment_amount)

	def on_submit(self):
		self.make_gl_entries()


	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
		make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
		# frappe.db.set(self, 'status', 'Cancelled')

	def make_gl_entries(self):
		if not self.investment_profit:
			return

		gl_entries = []

		# GL entry for profit and loss account associated with the project
		gl_entries.append(
			self.get_gl_dict(
				{
					"account": self.profit_and_loss_account_to_project,
					"debit": self.investment_profit,
					"debit_in_account_currency": self.investment_profit,
					"against": ",".join([d.account for d in self.contract_dividend_ratios]),
					"against_voucher_type": self.doctype,
					"against_voucher": self.name,
					"project": self.project,
					"posting_date":self.end_date,
					"remarks": "اغلاق المشاريع"
				},
				item=self,
			)
		)

		# GL entries for divided amounts
		for divided in self.contract_dividend_ratios:
			gl_entries.append(
				self.get_gl_dict(
					{
						"account": divided.account,
						"party_type": divided.party_type,
						"party": divided.party_name,
						"credit": divided.profit_amount,
						"credit_in_account_currency": divided.profit_amount,
						"against": self.profit_and_loss_account_to_project,
						"project": self.project,
						"remarks": "توزيع ارباح الصفقة",
						"against_voucher": self.name,
						"posting_date":self.end_date,
						"against_voucher_type": self.doctype
					},
					item=divided,
				)
			)

		make_gl_entries(
			gl_entries,
			# cancel=1,
			cancel=(self.docstatus == 2),
			update_outstanding="No",
			merge_entries=False,
		)


def get_status(start_date, end_date):
	"""
	Get a Contract's status based on the start, current and end dates

	Args:
	        start_date (str): The start date of the contract
	        end_date (str): The end date of the contract

	Returns:
	        str: 'Active' if within range, otherwise 'Inactive'
	"""

	if not end_date:
		return "Active"

	start_date = getdate(start_date)
	end_date = getdate(end_date)
	now_date = getdate(nowdate())

	return "Active" if start_date <= now_date <= end_date else "Inactive"


def update_status_for_contracts():
	"""
	Run the daily hook to update the statuses for all signed
	and submitted Contracts
	"""

	contracts = frappe.get_all(
		"investor Contract",
		filters={"is_signed": True, "docstatus": 1},
		fields=["name", "start_date", "end_date"],
	)

	for contract in contracts:
		status = get_status(contract.get("start_date"), contract.get("end_date"))

		frappe.db.set_value("investor Contract", contract.get("name"), "status", status)



def get_account_balance(account, project,cost_center = None):
    cond = ["is_cancelled=0"]

    if account:
        acc = frappe.get_doc("Account", account)
        # Check if the account is a group or a ledger
        if acc.is_group:
            cond.append(
                """exists (
                select name from `tabAccount` ac where ac.name = gle.account
                and ac.lft >= %s and ac.rgt <= %s
            )"""
                % (acc.lft, acc.rgt)
            )
        else:
            cond.append("gle.account = %s" % (frappe.db.escape(account, percent=False)))

    if cost_center:
        cond.append("gle.cost_center = %s" % (frappe.db.escape(cost_center, percent=False)))

    if project:
        cond.append("gle.project = %s" % (frappe.db.escape(project, percent=False)))

    select_field = "sum(debit) - sum(credit)"
    balance = frappe.db.sql(
        """
        SELECT {0}
        FROM `tabGL Entry` gle
        WHERE {1}
        """.format(
            select_field, " AND ".join(cond)
        )
    )[0][0]

    return flt(balance) if balance else 0.0


