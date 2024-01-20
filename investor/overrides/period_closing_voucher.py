
import frappe
from frappe import _

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from frappe.query_builder.functions import Sum
from frappe.utils import add_days, flt

from erpnext.accounts.doctype.period_closing_voucher.period_closing_voucher import PeriodClosingVoucher

class PeriodClosingVoucherCustom(PeriodClosingVoucher):
	@frappe.whitelist()
	
	def get_balances_based_on_dimensions(
		self, group_by_account=False, report_type=None, for_aggregation=False, get_opening_entries=False
	):
		"""Get balance for dimension-wise pl accounts"""

		qb_dimension_fields = ["cost_center", "finance_book", "project"]

		self.accounting_dimensions = get_accounting_dimensions()
		for dimension in self.accounting_dimensions:
			qb_dimension_fields.append(dimension)

		if group_by_account:
			qb_dimension_fields.append("account")

		account_filters = {
			"company": self.company,
			"is_group": 0,
		}

		if report_type:
			account_filters.update({"report_type": report_type})

		accounts = frappe.get_all("Account", filters=account_filters, pluck="name")

		gl_entry = frappe.qb.DocType("GL Entry")
		query = frappe.qb.from_(gl_entry).select(gl_entry.account, gl_entry.account_currency)
  
  
		if self.project:
			query = query.where(gl_entry.project == self.project)
   
		if not for_aggregation:
			query = query.select(
				(Sum(gl_entry.debit_in_account_currency) - Sum(gl_entry.credit_in_account_currency)).as_(
					"bal_in_account_currency"
				),
				(Sum(gl_entry.debit) - Sum(gl_entry.credit)).as_("bal_in_company_currency"),
			)
		else:
			query = query.select(
				(Sum(gl_entry.debit_in_account_currency)).as_("debit_in_account_currency"),
				(Sum(gl_entry.credit_in_account_currency)).as_("credit_in_account_currency"),
				(Sum(gl_entry.debit)).as_("debit"),
				(Sum(gl_entry.credit)).as_("credit"),
			)

		for dimension in qb_dimension_fields:
			query = query.select(gl_entry[dimension])

		query = query.where(
			(gl_entry.company == self.company)
			& (gl_entry.is_cancelled == 0)
			& (gl_entry.account.isin(accounts)) 
			# & (gl_entry.project == self.project) 
		)
		

		if get_opening_entries:
			query = query.where(
				gl_entry.posting_date.between(self.get("year_start_date"), self.posting_date)
				| gl_entry.is_opening
				== "Yes"
			)
		else:
			query = query.where(
				gl_entry.posting_date.between(self.get("year_start_date"), self.posting_date)
				& gl_entry.is_opening
				== "No"
			)

		if for_aggregation:
			query = query.where(gl_entry.voucher_type != "Period Closing Voucher")

		for dimension in qb_dimension_fields:
			query = query.groupby(gl_entry[dimension])

		return query.run(as_dict=1)


	def make_reverse_gl_entries(voucher_type, voucher_no):
		from erpnext.accounts.general_ledger import make_reverse_gl_entries

		try:
			make_reverse_gl_entries(voucher_type=voucher_type, voucher_no=voucher_no)
			frappe.db.set_value("Period Closing Voucher", voucher_no, "gle_processing_status", "Completed")
		except Exception as e:
			frappe.db.rollback()
			frappe.log_error(e)
			frappe.db.set_value("Period Closing Voucher", voucher_no, "gle_processing_status", "Failed")
	
 
@frappe.whitelist()
def get_gl_entries(self):
		frappe.msgprint("----------get_gl_entries-----------")
		for acc in get_balances_based_on_dimensions(self,
			group_by_account=False, report_type="Profit and Loss",posting_date= self.posting_date
		):

			if flt(acc.bal_in_company_currency):
				frappe.msgprint("----------bal_in_company_currency-----------")
				frappe.msgprint(str(acc.bal_in_company_currency))
				frappe.msgprint("---------------------")

