from frappe import _
import frappe
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.utils import cint, cstr, flt, formatdate, getdate, now

          
            
            
def create_purchase_invoice_from_landed_cost(doc, method):
    settings = frappe.get_single("Landed Cost Voucher setting")
    auto_submit = settings.is_auto_submit 

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
        custom_is_paid = doc.custom_is_paid
        custom_mode_of_payment = doc.custom_mode_of_payment
        custom_paid_amount = doc.custom_paid_amount
        posting_date = doc.posting_date
        custom_payment_account = doc.custom_payment_account
    
    for item in doc.items:
        remarks += item.description + ":> "+ str(item.applicable_charges) + "|| "

    for tax in doc.taxes:
        if tax.custom_purchase_invoice:
            return
        if not tax.custom_supplier:
            return
        purchase_invoice = create_purchase_invoice(tax, cost_center, project,custom_is_paid,custom_mode_of_payment,custom_paid_amount,posting_date,custom_payment_account)
        remarks += tax.description + "| " 
        try:
            purchase_invoice.remarks = remarks
            purchase_invoice.insert()
            if auto_submit:
                purchase_invoice.submit()
            # purchase_invoice.submit()
            # tax.purchase_invoice = purchase_invoice.name
            tax.db_set('custom_purchase_invoice', purchase_invoice.name, update_modified=False)
            # return purchase_invoice.name
        except frappe.exceptions.ValidationError as e:
            error_message = "Error creating purchase invoice for supplier {0}: {1}".format(tax.custom_supplier, str(e))
            frappe.throw(error_message)

def create_purchase_invoice(tax, cost_center, project,custom_is_paid,custom_mode_of_payment,custom_paid_amount,posting_date,custom_payment_account):
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
    purchase_invoice.posting_date = posting_date
    purchase_invoice.posting_date = posting_date
    purchase_invoice.set_posting_time = 1
    purchase_invoice.cost_center = cost_center
    purchase_invoice.project = project
    purchase_invoice.is_paid = custom_is_paid
    purchase_invoice.mode_of_payment = custom_mode_of_payment
    purchase_invoice.paid_amount = custom_paid_amount
    purchase_invoice.cash_bank_account = custom_payment_account

    
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
    frappe.msgprint("hs")
   
    doc.custom_total_due_to_suppliers = doc.custom_project_cost - doc.custom_total_paid_to_suppliers if doc.custom_project_cost else 0
    
    total_cost_of_items_sold = doc.custom_total_cost_of_items_sold or 0
    total_received_in_deal = doc.custom_total_received_in_deal or 0
    total_due_to_suppliers = doc.custom_total_due_to_suppliers or 0


    if doc.custom_total_received_in_deal != 0:
        doc.custom_total_available_in_deal = min(total_received_in_deal, total_due_to_suppliers)
        doc.custom_total_available_for_funding_other_deals = total_received_in_deal - doc.custom_total_available_in_deal
    if doc.custom_investment_contracts:
        total_funding_amount = sum(contract.investment_amount for contract in doc.custom_investment_contracts)
        doc.custom_funding_amount_ = total_funding_amount
        doc.custom_financing_gap=total_funding_amount-doc.custom_project_cost

    # if doc.custom_profit_and_loss_account_to_project:
    #     balanc = get_account_balance(account = doc.profit_and_loss_account_to_project, project = doc.project)
    #     doc.project_profit = balanc
    # doc.custom_project_amount = 
    # doc.custom_project_amount = doc.total_purchase_cost
    if doc.custom_project_amount and doc.custom_investment_contracts:
       
        for contract in doc.custom_investment_contracts:
            contract.investment_percent = ( contract.investment_amount * 100) / doc.custom_project_cost
            contract.gross_margin = ( doc.custom_project_amount * contract.investment_percent) / 100
            contract.per_gross_margin = ( contract.gross_margin * 100) / contract.investment_amount
            total_investment_percentage = sum(contract.investment_percent for contract in doc.custom_investment_contracts)
            if doc.custom_total_profit:
                contract.net_profit = (contract.investment_percent / total_investment_percentage) * doc.custom_total_profit if doc.custom_total_profit else 0


            if doc.custom_total_cost_of_items_sold:
                    contract.cost_of_items_sold = (contract.investment_percent / total_investment_percentage) * doc.custom_total_cost_of_items_sold if doc.custom_total_cost_of_items_sold else 0
                    contract.available_in_same_deal = (contract.investment_percent / total_investment_percentage) * doc.custom_total_available_in_deal if doc.custom_total_available_in_deal else 0
                    contract.available_for_other_deals = (contract.investment_percent / total_investment_percentage) * doc.custom_total_available_for_funding_other_deals if doc.custom_total_available_for_funding_other_deals else 0
                    contract.used_for_other_deals = (contract.investment_percent / total_investment_percentage) * doc.custom_total_available_for_use_in_deal if doc.custom_total_available_for_use_in_deal else 0
            investor_contract = frappe.get_doc("investor Contract", contract.investor_contract)
            investor_contract.project_profit = doc.custom_project_amount
            investor_contract.project = doc.name
            investor_contract.project_name = doc.project_name
            investor_contract.project_cost = doc.custom_project_cost
            investor_contract.total_cost_of_items_sold = contract.cost_of_items_sold
            investor_contract.investment_percent = contract.investment_percent
            investor_contract.investment_profit = contract.gross_margin
            investor_contract.funding_available = contract.available_in_same_deal
            investor_contract.available_for_other_deals = contract.available_for_other_deals
            investor_contract.used_for_other_deals = contract.used_for_other_deals
            investor_contract.net_profit = contract.net_profit
            investor_contract.profit_and_loss_account_to_project = doc.custom_profit_and_loss_account_to_project
            investor_contract.save()
            frappe.db.commit()

            for ratio in investor_contract.contract_dividend_ratios:
                    profit_amount = (contract.gross_margin * ratio.dividend) / 100
                    ratio.profit_amount = profit_amount  
                    ratio.save()
                    frappe.db.commit()

                    # frappe.msgprint(f"مشارك بنسبة {ratio.dividend}% سيحصل على ربح قدره {profit_amount} من إجمالي الربح")
   

        

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
from frappe import _, msgprint, qb, scrub
from erpnext.accounts.party import (
    get_party_gle_currency, 
    get_party_gle_account, 
    get_party_advance_account, 
)


@frappe.whitelist()
def get_party_account(party_type, party=None, company=None, include_advance=False):
   
    """Returns the account for the given `party`.
    Will first search in party (Customer / Supplier / Investor) record, if not found,
    will search in group (Customer Group / Supplier Group / Investor Group),
    finally will return default."""
    
    if not company:
        frappe.throw(_("Please select a Company"))

    if not party and party_type in ["Customer", "Supplier", "Investor"]:
        default_account_name = {
            "Customer": "default_receivable_account",
            "Supplier": "default_payable_account",
            "Investor": "default_investor_account",  
        }.get(party_type)

        return frappe.get_cached_value("Company", company, default_account_name)

    account = frappe.db.get_value(
        "Party Account", {"parenttype": party_type, "parent": party, "company": company}, "account"
    )

    if not account and party_type in ["Customer", "Supplier", "Investor"]:
        party_group_doctype = {
            "Customer": "Customer Group",
            "Supplier": "Supplier Group",
            "Investor": "Investor Group", 
        }.get(party_type)

        group = frappe.get_cached_value(party_type, party, scrub(party_group_doctype))
        account = frappe.db.get_value(
            "Party Account",
            {"parenttype": party_group_doctype, "parent": group, "company": company},
            "account",
        )

    if not account and party_type in ["Customer", "Supplier", "Investor"]:
        default_account_name = {
            "Customer": "default_receivable_account",
            "Supplier": "default_payable_account",
            "Investor": "default_investor_account", 
        }.get(party_type)

        account = frappe.get_cached_value("Company", company, default_account_name)

    existing_gle_currency = get_party_gle_currency(party_type, party, company)
    if existing_gle_currency:
        if account:
            account_currency = frappe.get_cached_value("Account", account, "account_currency")
        if (account and account_currency != existing_gle_currency) or not account:
            account = get_party_gle_account(party_type, party, company)

    if include_advance and party_type in ["Customer", "Supplier", "Investor"]:
        advance_account = get_party_advance_account(party_type, party, company)
        if advance_account:
            return [account, advance_account]
        else:
            return [account]

    return account
@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc
    def update_item(source, target, source_parent):
        target.party_type = "Investor"
        target.party = source.party_name
        target.party_name = source.party_name
        target.paid_to = source.investor_account
        target.payment_type = "Pay"
        target.paid_amount = source.investment_profit
        account_currency = frappe.db.get_value("Account", source.investor_account, "account_currency")
        target.paid_from_account_currency = account_currency
        target.paid_to_account_currency = account_currency


    doc = get_mapped_doc(
        "investor Contract",  
        source_name,
        {
            "investor Contract": {
                "doctype": "Payment Entry",
                "field_map": {
                    
                  
                   
                },
                "postprocess": update_item,
            },
        },
        target_doc
    )

    return doc
@frappe.whitelist()
def update_project_status_on_invoice_submission(doc, method):
    if doc.project:
        project = frappe.get_doc("Project", doc.project)
        
        if project.status == "Open":
            project.status = "In Progress"
            project.save()

            for contract in project.custom_investment_contracts:
                contract_doc = frappe.get_doc("investor Contract", contract.investor_contract)
                if contract_doc.status != "Active":
                    contract_doc.status = "Active"
                    contract_doc.save()
            
            frappe.db.commit()
    #         frappe.msgprint(f"تم تغيير حالة المشروع {project.name} إلى In Progress وتفعيل العقود المرتبطة.")
    #     else:
    #         frappe.msgprint(f"المشروع {project.name} لا يمكن تغيير حالته لأنه ليس في الحالة المفتوحة أو الفاتورة تحتوي على قيمة تكاليف شراء.")
    # else:
    #     frappe.msgprint("لا توجد مشاريع مرتبطة بهذه الفاتورة.")
@frappe.whitelist()
def on_submit_payment_entry(payment_entry, method):

    update_project_payment_totals(payment_entry, method)

    # update_investor_contract_status(payment_entry, method)
    update_project_received_totals(payment_entry, method)
@frappe.whitelist()
def on_submit_parchase_invoice(doc, method):
    # update_project_received_totals(doc, method)
    update_project_status_on_invoice_submission(doc, method)

@frappe.whitelist()
def update_investor_contract_status(doc, method):
     if doc.investor_contract:
       
            contract = frappe.get_doc("investor Contract", doc.investor_contract)
            contract.status = "Complete"
            contract.save()
            frappe.db.commit()
            frappe.msgprint("🎉 Congratulations! The contract status has been Done successfully.")

@frappe.whitelist()
# def update_project_payment_totals(payment_entry, method):

#     if not payment_entry.project:
#         return  

#     total_paid = frappe.db.sql("""
#         SELECT SUM(paid_amount) 
#         FROM `tabPayment Entry` 
#         WHERE project = %s AND payment_type = 'Pay'
#     """, (payment_entry.project))[0][0] or 0

#     project = frappe.get_doc("Project", payment_entry.project)

#     total_due = project.estimated_costing - total_paid if project.estimated_costing else 0

#     frappe.db.set_value("Project", payment_entry.project, "custom_total_paid_to_suppliers", total_paid)
#     frappe.db.set_value("Project", payment_entry.project, "custom_total_due_to_suppliers", total_due)

@frappe.whitelist()
def update_project_payment_totals(doc, method):

    project = None

    if hasattr(doc, 'project') and doc.project:
        project = doc.project
        project_doc = frappe.get_doc("Project", project) 
        update_dividend_project_investor(project_doc, "custom") 

    else:
        if doc.doctype == "Journal Entry":
            related_purchase_invoice = frappe.db.sql("""
                SELECT reference_name
                FROM `tabJournal Entry Account`
                WHERE docstatus = 1 AND account_type = 'Payable' 
                AND reference_type = 'Purchase Invoice' 
                AND parent = %s
            """, (doc.name,), as_dict=True)

            if related_purchase_invoice:
                purchase_invoice = frappe.get_doc("Purchase Invoice", related_purchase_invoice[0].reference_name)
                project = purchase_invoice.project

    if not project:
        return  

    total_paid_pe = frappe.db.sql("""
        SELECT SUM(paid_amount) 
        FROM `tabPayment Entry` 
        WHERE project = %s AND payment_type = 'Pay' AND docstatus = 1
    """, (project,))[0][0] or 0

    total_paid_pi = frappe.db.sql("""
        SELECT SUM(paid_amount) 
        FROM `tabPurchase Invoice` 
        WHERE project = %s AND docstatus = 1
    """, (project,))[0][0] or 0

    total_paid_je = frappe.db.sql("""
        SELECT SUM(debit) 
        FROM `tabJournal Entry Account` 
        WHERE docstatus = 1 AND account_type = 'Payable' 
        AND reference_name IN (
            SELECT name FROM `tabPurchase Invoice` WHERE project = %s AND docstatus = 1
        )
    """, (project,))[0][0] or 0

    total_paid = total_paid_pe + total_paid_pi + total_paid_je

    frappe.db.set_value("Project", project, "custom_total_paid_to_suppliers", total_paid)

    custom_project_cost = frappe.db.get_value("Project", project, "custom_project_cost") or 0
    total_due = custom_project_cost - total_paid if custom_project_cost else 0

    frappe.db.set_value("Project", project, "custom_total_due_to_suppliers", total_due)
    custom_funding_amount = frappe.db.get_value("Project", project, "custom_funding_amount_") or 0

    total_available_in_deal = frappe.db.get_value("Project", project, "custom_total_available_in_deal") or 0

    if custom_funding_amount < total_paid:
        payment_amount = doc.paid_amount 

        if payment_amount <= total_available_in_deal:
            custom_total_used_return_from_deal_cost = frappe.db.get_value("Project", project, "custom_total_used_return_from_deal_cost") or 0
            new_used_return = custom_total_used_return_from_deal_cost + payment_amount

            frappe.db.set_value("Project", project, "custom_total_used_return_from_deal_cost", new_used_return)
            frappe.db.set_value("Project", project, "custom_total_available_in_deal", total_available_in_deal - payment_amount)
    #     else:
    #         frappe.throw(f"Payment of {payment_amount} is not allowed because it exceeds available Project ({project}) profits ({total_available_in_deal})!")

    frappe.db.commit()
   

@frappe.whitelist()
def update_project_received_total(doc, method):
    if not doc.project:
        return
    
    total_received = 0
    total_paid_to_suppliers = 0

    sales_invoices = frappe.get_all(
        "Sales Invoice",
        filters={"project": doc.project, "docstatus": 1}, 
        fields=["name", "grand_total", "outstanding_amount"]
    )

    for invoice in sales_invoices:
        paid_amount = invoice.grand_total - invoice.outstanding_amount
        total_received += paid_amount

    purchase_invoices = frappe.get_all(
        "Purchase Invoice",
        filters={"project": doc.project, "docstatus": 1}, 
        fields=["name", "grand_total", "outstanding_amount"]
    )

    for invoice in purchase_invoices:
        paid_amount = invoice.grand_total - invoice.outstanding_amount
        total_paid_to_suppliers += paid_amount

    project_doc = frappe.get_doc("Project", doc.project)
    
    project_doc.custom_total_paid_to_suppliers = total_paid_to_suppliers
    
    project_doc.custom_total_due_to_suppliers = (project_doc.custom_project_cost or 0) - total_paid_to_suppliers

    project_doc.custom_total_received_in_deal = total_received  

    update_dividend_project_investor(project_doc, "custom")

    project_doc.db_update()
    
   

    return {
        "total_received": total_received,
        "total_paid_to_suppliers": total_paid_to_suppliers,
        "total_due_to_suppliers": project_doc.custom_total_due_to_suppliers
    }


@frappe.whitelist()
def validate_payment_entry(doc, method):
    if not doc.project:
        return
    if doc.payment_type != "Pay":
        return

    project_doc = frappe.get_doc("Project", doc.project)

    project_funding = project_doc.custom_funding_amount_ or 0
    available_amount = project_doc.custom_total_available_in_deal or 0
    total_project_budget = project_funding + available_amount

    total_paid_to_suppliers = project_doc.custom_total_paid_to_suppliers or 0

    total_payment_amount = doc.base_paid_amount

    total_after_payment = total_paid_to_suppliers + total_payment_amount
    if total_after_payment > total_project_budget:
        exceeded_amount = total_after_payment - total_project_budget
        frappe.throw(
            f"Payment for Project '{project_doc.name}' is not Allowed! The total payments ({total_after_payment}) exceed the project budget ({total_project_budget}) by {exceeded_amount}."
        )

    



@frappe.whitelist()
def update_project_received_totals(doc, method):
    project = None

    if hasattr(doc, 'project') and doc.project:
        project = doc.project
        project_doc = frappe.get_doc("Project", project)  
        update_dividend_project_investor(project_doc, "custom")
        frappe.msgprint(f"it is for pro {project}")


    else:
        frappe.msgprint(f"it is for prfo {project}")
        if doc.doctype == "Journal Entry":
            related_sales_invoice = frappe.db.sql("""
                SELECT reference_name
                FROM `tabJournal Entry Account`
                WHERE docstatus = 1 AND account_type = 'Receivable' 
                AND reference_type = 'Sales Invoice' 
                AND parent = %s
            """, (doc.name,), as_dict=True)

            if related_sales_invoice:
                sales_invoice = frappe.get_doc("Sales Invoice", related_sales_invoice[0].reference_name)
                project = sales_invoice.project

    if not project:
        return  

    total_received_pe = frappe.db.sql("""
        SELECT SUM(paid_amount) 
        FROM `tabPayment Entry` 
        WHERE project = %s AND payment_type = 'Receive' AND docstatus = 1
    """, (project,))[0][0] or 0

    total_received_si = frappe.db.sql("""
        SELECT SUM(paid_amount) 
        FROM `tabSales Invoice` 
        WHERE project = %s AND docstatus = 1
    """, (project,))[0][0] or 0

    total_received_je = frappe.db.sql("""
        SELECT SUM(credit) 
        FROM `tabJournal Entry Account` 
        WHERE docstatus = 1 AND account_type = 'Receivable' 
        AND reference_name IN (
            SELECT name FROM `tabSales Invoice` WHERE project = %s AND docstatus = 1
        )
    """, (project,))[0][0] or 0

    total_received = total_received_pe + total_received_si + total_received_je
    frappe.msgprint(f"it is {total_received} for pro {project}")

    frappe.db.set_value("Project", project, "custom_total_received_in_deal", total_received)
    frappe.db.commit()

   


from frappe.utils import nowdate

def process_project_closure1(doc, method):

    # التحقق من الحقل المخصص للمشروع
    # if not doc.custom_project:
       
    #     return

    investment_contracts = frappe.get_all(
        "Investment Contracts",
        filters={
            "parent": doc.custom_project,
          
        },
        fields=["investor_contract"]
    )

    if not investment_contracts:
        return

    for contract_data in investment_contracts:
        contract_name = contract_data.get("investor_contract")
        if contract_name:
            invoke_gl_entry(contract_name)

from investor.investor.doctype.investor_contract.investor_contract import investorContract

def invoke_gl_entry(contract_name):
  
        contract_doc = frappe.get_doc("investor Contract", contract_name)
        
        if hasattr(contract_doc, "make_gl_entries"):
            contract_doc.make_gl_entries()
            contract_doc.status = "Fulfilled"
            contract_doc.save()
            frappe.db.commit()

@frappe.whitelist()
def map_investor_contract(source_name, target_doc=None):
    import frappe

    source_doc = frappe.get_doc("investor Contract", source_name)

    if not source_doc:
        frappe.throw("Investor Contract not found")

    if not target_doc:
        target_doc = frappe.new_doc("investor Contract") 

    target_doc.party_name = source_doc.party_name
    target_doc.funding_available = source_doc.funding_available 
    target_doc.project = source_doc.project
    target_doc.project_name = source_doc.project_name

    return target_doc

import frappe
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults


@frappe.whitelist()
def get_item_expense_account(item_code, company):
    expense_account = None

   
    item_defaults = get_item_defaults(item_code, company)
    if item_defaults:
        expense_account = item_defaults.get("expense_account")

    if not expense_account:
        item_doc = frappe.get_doc("Item", item_code) 
        item_group = item_doc.item_group 

        if item_group and frappe.db.exists("Item Group", item_group): 
            item_group_defaults = get_item_group_defaults(item_code, company)
            if item_group_defaults:
                expense_account = item_group_defaults.get("expense_account")

    if not expense_account and frappe.db.exists("Company", company):
        company_doc = frappe.get_doc("Company", company)
        expense_account = company_doc.get("default_expense_account")

   
    return {"expense_account": expense_account}
