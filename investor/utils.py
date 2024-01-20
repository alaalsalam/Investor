from frappe import _
import frappe
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.utils import cint, cstr, flt, formatdate, getdate, now

          
            
            
def create_purchase_invoice_from_landed_cost(doc, method):

    remarks = ""
    cost_center = ""
    project = ""
    doctype = ""
    # Retrieve the latest purchase invoice from the purchase_receipts table
    for purchase in doc.purchase_receipts:
        purchase_name = purchase.receipt_document
        doctype = purchase.receipt_document_type
        
    purchase = frappe.get_list(
        doctype,
        filters={"docstatus": 1, "name": purchase_name},
        fields=["name", "cost_center", "project"],
        order_by="modified desc",
        limit=1
    )
    
    
    if purchase:
        cost_center = purchase[0].cost_center
        project = purchase[0].project
    
    for item in doc.items:
        remarks += item.description + ":> "+ str(item.applicable_charges) + "|| "

    for tax in doc.taxes:
        if tax.custom_purchase_invoice:
            return
        purchase_invoice = create_purchase_invoice(tax, cost_center, project)
        remarks += tax.description + "| " 
        try:
            purchase_invoice.remarks = remarks
            purchase_invoice.insert()
            purchase_invoice.submit()
            # tax.purchase_invoice = purchase_invoice.name
            tax.db_set('custom_purchase_invoice', purchase_invoice.name, update_modified=False)
            # return purchase_invoice.name
        except frappe.exceptions.ValidationError as e:
            error_message = "Error creating purchase invoice for supplier {0}: {1}".format(tax.custom_supplier, str(e))
            frappe.throw(error_message)

def create_purchase_invoice(tax, cost_center, project):
    """
    Create a new purchase invoice for a specific tax.

    Args:
        tax (frappe.model.document.Document): The tax associated with the purchase invoice.
        cost_center (str): The cost center to be set in the purchase invoice.
        project (str): The project to be set in the purchase invoice.

    Returns:
        frappe.model.document.Document: The created purchase invoice.
    """
    purchase_invoice = frappe.new_doc("Purchase Invoice")
    purchase_invoice.supplier = tax.custom_supplier
    purchase_invoice.cost_center = cost_center
    purchase_invoice.project = project
    
    purchase_invoice.currency = tax.account_currency
    purchase_invoice.conversion_rate = tax.exchange_rate
    
    purchase_invoice.append("items", {
        "item_code": tax.custom_item_code,
        "qty": 1,
        "rate": tax.amount,
        "expense_account": tax.expense_account,
        "project":project
        # Add other item details as required
    })
    return purchase_invoice



def update_item_account(doc, method):
    for i in doc.taxes:
        if i.custom_item_code:
            get_item_account(doc, method)
            
def get_item_account(doc, method):
        for entry in doc.taxes:
            item = get_item_defaults(entry.custom_item_code, doc.company)
            item_group = get_item_group_defaults(entry.custom_item_code, doc.company)
            entry.expense_account = item.get("expense_account") or item_group.get("expense_account")

         
def update_dividend_project_investor(doc, method):
    # if doc.custom_profit_and_loss_account_to_project:
    #     balanc = get_account_balance(account = doc.profit_and_loss_account_to_project, project = doc.project)
    #     doc.project_profit = balanc
    # doc.custom_project_amount = 
    # doc.custom_project_amount = doc.total_purchase_cost
    if doc.custom_project_amount and doc.custom_investment_contracts:
        for contract in doc.custom_investment_contracts:
            contract.investment_percent = ( contract.investment_amount * 100) / doc.estimated_costing
            contract.gross_margin = ( doc.custom_project_amount * contract.investment_percent) / 100
            contract.per_gross_margin = ( contract.gross_margin * 100) / contract.investment_amount
            investor_contract = frappe.get_doc("investor Contract", contract.investor_contract)
            investor_contract.project_profit = doc.custom_project_amount
            investor_contract.investment_percent = contract.investment_percent
            investor_contract.investment_profit = contract.gross_margin
            investor_contract.save()


        

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