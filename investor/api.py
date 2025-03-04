
import frappe
from frappe import _
import json
from erpnext.stock.stock_ledger import get_previous_sle


@frappe.whitelist()
def get_actual_qty(data_dic):

    previous_sle = get_previous_sle(json.loads(data_dic))
    return previous_sle

@frappe.whitelist()
def get_items_from_purchase_receipts_new(self):
    self.set("items", [])
    for pr in self.get("purchase_receipts"):
        if pr.receipt_document_type and pr.receipt_document:
            pr_items = frappe.db.sql(
                """select pr_item.item_code, pr_item.description,
                pr_item.qty, pr_item.base_rate, pr_item.base_amount, pr_item.name,
                pr_item.cost_center, pr_item.is_fixed_asset
                from `tab{doctype} Item` pr_item where parent = %s
                and exists(select name from tabItem
                    where name = pr_item.item_code and (is_stock_item = 1 or is_fixed_asset=1))
                """.format(
                    doctype=pr.receipt_document_type
                ),
                pr.receipt_document,
                as_dict=True,
            )

            for d in pr_items:
                item = self.append("items")
                item.item_code = d.item_code
                item.description = d.description
                item.qty = d.qty
                item.rate = d.base_rate
                item.cost_center = d.cost_center or erpnext.get_default_cost_center(self.company)
                item.amount = d.base_amount
                item.receipt_document_type = pr.receipt_document_type
                item.receipt_document = pr.receipt_document
                item.purchase_receipt_item = d.name
                item.is_fixed_asset = d.is_fixed_asset

@frappe.whitelist()
def delete_account_closing_balance_docs():
    account_closing_balance_docs = frappe.get_all('Account Closing Balance', fields=['name'])
    
    for doc in account_closing_balance_docs:
        try:
            frappe.delete_doc('Account Closing Balance', doc['name'], force=1)
            frappe.db.commit()
            print(f"Deleted: {doc['name']}")
        except Exception as e:
            print(f"Failed to delete {doc['name']}: {e}")

import frappe
from frappe.utils import getdate
from erpnext.accounts.doctype.period_closing_voucher.period_closing_voucher import PeriodClosingVoucher


@frappe.whitelist()
def cancel_period_closing_vouchers():
    period_year = 2025

    vouchers = frappe.get_all(
        "Period Closing Voucher",
        filters={"fiscal_year": ["like", f"{period_year}%"]}, 
        fields=["name"]
    )
    
    for voucher in vouchers:
        doc = frappe.get_doc("Period Closing Voucher", voucher.name)
        if doc.docstatus == 1:
            doc.cancel() 
        else:
            frappe.msgprint(f"Voucher {voucher.name} is already canceled.")
    
    frappe.db.commit()
    return f"Canceled {len(vouchers)} Period Closing Vouchers for {period_year}."


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

from frappe.utils import today
@frappe.whitelist()
def create_sub_contracts(project_name, investment_amount):
    investment_amount = float(investment_amount)
    project = frappe.get_doc("Project", project_name)
    available_funds = project.custom_total_available_for_funding_other_deals or 0

    if investment_amount > available_funds:
        frappe.throw(f"Investment amount {investment_amount} exceeds available funding {available_funds} for project {project_name}.")

    contracts = frappe.get_all(
        "Investment Contracts",
        filters={"parent": project_name, "contract_type": "Open"},
        fields=["investor_contract"]
    )

    if not contracts:
        frappe.throw("No Open Investment Contracts found for the selected project.")

    open_contracts_count = len(contracts)

    divided_amount = investment_amount / open_contracts_count
    created_contracts = []

    
    for contract in contracts:
        investor_contract = frappe.get_doc("investor Contract", contract["investor_contract"])

        sub_contract = frappe.get_doc({
            "doctype": "investor Contract",
            "party_name": investor_contract.party_name,
            "investor_account": investor_contract.investor_account,
            "contract_terms": investor_contract.name,
            "contract_type": "Sub Contract",
            "investment_amount": divided_amount,
            "posting_date": today(),
            "docstatus": 1  # Submitted
        })

        sub_contract.insert()
        frappe.db.commit()
        created_contracts.append({
                "investor_contract": sub_contract.name,
                "investor_name": investor_contract.party_name,
                "investment_amount": divided_amount,
                "contract_type": "Sub Contract"
            })


    project.custom_total_available_for_use_in_deal += investment_amount
    project.custom_total_available_for_funding_other_deals -= investment_amount
    project.db_update()
    return created_contracts 