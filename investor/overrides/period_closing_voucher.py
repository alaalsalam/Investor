
import frappe
from frappe import _

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from frappe.query_builder.functions import Sum
from frappe.utils import add_days, flt

from erpnext.accounts.doctype.period_closing_voucher.period_closing_voucher import PeriodClosingVoucher

# class PeriodClosingVoucherCustom(PeriodClosingVoucher):
# 	@frappe.whitelist()
	
# 	def get_balances_based_on_dimensions(
# 		self, group_by_account=False, report_type=None, for_aggregation=False, get_opening_entries=False
# 	):
# 		"""Get balance for dimension-wise pl accounts"""

# 		qb_dimension_fields = ["cost_center", "finance_book", "project"]

# 		self.accounting_dimensions = get_accounting_dimensions()
# 		for dimension in self.accounting_dimensions:
# 			qb_dimension_fields.append(dimension)

# 		if group_by_account:
# 			qb_dimension_fields.append("account")

# 		account_filters = {
# 			"company": self.company,
# 			"is_group": 0,
# 		}

# 		if report_type:
# 			account_filters.update({"report_type": report_type})

# 		accounts = frappe.get_all("Account", filters=account_filters, pluck="name")

# 		gl_entry = frappe.qb.DocType("GL Entry")
# 		query = frappe.qb.from_(gl_entry).select(gl_entry.account, gl_entry.account_currency)
  
  
# 		if self.project:
# 			query = query.where(gl_entry.project == self.project)
   
# 		if not for_aggregation:
# 			query = query.select(
# 				(Sum(gl_entry.debit_in_account_currency) - Sum(gl_entry.credit_in_account_currency)).as_(
# 					"bal_in_account_currency"
# 				),
# 				(Sum(gl_entry.debit) - Sum(gl_entry.credit)).as_("bal_in_company_currency"),
# 			)
# 		else:
# 			query = query.select(
# 				(Sum(gl_entry.debit_in_account_currency)).as_("debit_in_account_currency"),
# 				(Sum(gl_entry.credit_in_account_currency)).as_("credit_in_account_currency"),
# 				(Sum(gl_entry.debit)).as_("debit"),
# 				(Sum(gl_entry.credit)).as_("credit"),
# 			)

# 		for dimension in qb_dimension_fields:
# 			query = query.select(gl_entry[dimension])

# 		query = query.where(
# 			(gl_entry.company == self.company)
# 			& (gl_entry.is_cancelled == 0)
# 			& (gl_entry.account.isin(accounts)) 
# 			# & (gl_entry.project == self.project) 
# 		)
		

# 		if get_opening_entries:
# 			query = query.where(
# 				gl_entry.posting_date.between(self.get("year_start_date"), self.posting_date)
# 				| gl_entry.is_opening
# 				== "Yes"
# 			)
# 		else:
# 			query = query.where(
# 				gl_entry.posting_date.between(self.get("year_start_date"), self.posting_date)
# 				& gl_entry.is_opening
# 				== "No"
# 			)

# 		if for_aggregation:
# 			query = query.where(gl_entry.voucher_type != "Period Closing Voucher")

# 		for dimension in qb_dimension_fields:
# 			query = query.groupby(gl_entry[dimension])

# 		return query.run(as_dict=1)


# 	def make_reverse_gl_entries(voucher_type, voucher_no):
# 		from erpnext.accounts.general_ledger import make_reverse_gl_entries

# 		try:
# 			make_reverse_gl_entries(voucher_type=voucher_type, voucher_no=voucher_no)
# 			frappe.db.set_value("Period Closing Voucher", voucher_no, "gle_processing_status", "Completed")
# 		except Exception as e:
# 			frappe.db.rollback()
# 			frappe.log_error(e)
# 			frappe.db.set_value("Period Closing Voucher", voucher_no, "gle_processing_status", "Failed")
	
 
# @frappe.whitelist()
# def get_gl_entries(self):
# 		frappe.msgprint("----------get_gl_entries-----------")
# 		for acc in get_balances_based_on_dimensions(self,
# 			group_by_account=False, report_type="Profit and Loss",posting_date= self.posting_date
# 		):

# 			if flt(acc.bal_in_company_currency):
# 				frappe.msgprint("----------bal_in_company_currency-----------")
# 				frappe.msgprint(str(acc.bal_in_company_currency))
# 				frappe.msgprint("---------------------")

import frappe

from erpnext.accounts.doctype.period_closing_voucher.period_closing_voucher import PeriodClosingVoucher
from erpnext.accounts.general_ledger import get_accounting_dimensions

class PeriodClosingVoucherCustom(PeriodClosingVoucher):
    def on_submit(self):
        self.db_set("gle_processing_status", "In Progress")
        self.make_gl_entries()
        self.update_project_status()

    # @frappe.whitelist()
    # def get_account_balances_based_on_dimensions(self, report_type):
    #     """Get balance for dimension-wise pl accounts"""
    #     self.get_accounting_dimension_fields()
    #     acc_bal_dict = frappe._dict()
    #     gl_entries = []

    #     with frappe.db.unbuffered_cursor():
    #         gl_entries = self.get_gl_entries_for_current_period(report_type, as_iterator=True)
    #         for gle in gl_entries:
    #             if gle.custom_project == self.custom_project:  
    #                 acc_bal_dict = self.set_account_balance_dict(gle, acc_bal_dict)

    #     if report_type == "Balance Sheet" and self.is_first_period_closing_voucher():
    #         opening_entries = self.get_gl_entries_for_current_period(report_type, only_opening_entries=True)
    #         for gle in opening_entries:
    #             if gle.custom_project == self.custom_project:  
    #                 acc_bal_dict = self.set_account_balance_dict(gle, acc_bal_dict)

    #     return acc_bal_dict
    def get_gl_entries_for_current_period(self, report_type, only_opening_entries=False, as_iterator=False):
        date_condition = ""
        if only_opening_entries:
            date_condition = "is_opening = 'Yes'"
        else:
            date_condition = f"posting_date BETWEEN '{self.period_start_date}' AND '{self.period_end_date}' and is_opening = 'No'"

        project_condition = ""
        if self.custom_project:
            project_condition = f"AND project = '{self.custom_project}'"
        
        cost_center_condition = ""
        if self.custom_cost_center:
            cost_center_condition = f"AND cost_center = '{self.custom_cost_center}'"

        return frappe.db.sql(
            """
            SELECT
                name,
                posting_date,
                account,
                account_currency,
                debit_in_account_currency,
                credit_in_account_currency,
                debit,
                credit,
                {}
            FROM `tabGL Entry`
            WHERE
                {}
                {}
                {}
                AND company = %s
                AND voucher_type != 'Period Closing Voucher'
                AND EXISTS(SELECT name FROM `tabAccount` WHERE name = account AND report_type = %s)
                AND is_cancelled = 0
            """.format(
                ", ".join(self.accounting_dimension_fields),
                date_condition,
                project_condition,
                cost_center_condition
            ),
            (self.company, report_type),
            as_dict=1,
            as_iterator=as_iterator,
        )

    def get_previous_closed_period_in_current_year(fiscal_year, company):
        prev_closed_period_end_date = frappe.db.get_value(
            "Period Closing Voucher",
            filters={
                "company": company,
                "fiscal_year": fiscal_year,
                "docstatus": 1,
            },
            fieldname=["period_end_date"],
            order_by="period_end_date desc",
        )
        return prev_closed_period_end_date

    def validate_start_and_end_date(self):
        from frappe.utils import add_days, flt, formatdate, getdate

        self.fy_start_date, self.fy_end_date = frappe.db.get_value(
            "Fiscal Year", self.fiscal_year, ["year_start_date", "year_end_date"]
        )

        # prev_closed_period_end_date = self.get_previous_closed_period_in_current_year(
        #     self.fiscal_year, self.company
        # )
        # valid_start_date = (
        #     add_days(prev_closed_period_end_date, 1) if prev_closed_period_end_date else self.fy_start_date
        # )

        # # if getdate(self.period_start_date) != getdate(valid_start_date):
        # #     frappe.throw(_("Period Start Date must be {0}").format(formatdate(valid_start_date)))

        # if getdate(self.period_start_date) > getdate(self.period_end_date):
        #     frappe.throw(_("Period Start Date cannot be greater than Period End Date"))

        return
       
        
   
    def update_project_status(self, method=None):
       
        if self.custom_project:
            project = frappe.get_doc("Project", self.custom_project)
            if project:
                project.status = "Completed"
                project.save()
                frappe.db.commit()  
    