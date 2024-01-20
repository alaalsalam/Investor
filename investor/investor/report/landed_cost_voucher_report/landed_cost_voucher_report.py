# Copyright (c) 2023, alaalsalam and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def get_filters():
    return [
        {
            "fieldname": "from_date",
            "label": _("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": _("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "docstatus",
            "label": _("docstatus"),
            "fieldtype": "Select",
            "options": "\nDraft\nSubmitted\nCancelled",
            "default": "Submitted"
        },
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Item"
        },
        {
            "fieldname": "project",
            "label": _("project"),
            "fieldtype": "Link",
            "options": "project"
        },
        {
            "fieldname": "custom_item_code",
            "label": _("Custom Item Code"),
            "fieldtype": "Data"
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency"
        },
        {
            "fieldname": "account_currency",
            "label": _("Account Currency"),
            "fieldtype": "Link",
            "options": "Currency"
        },
        {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Data"
        },
        {
            "fieldname": "custom_purchase_invoice",
            "label": _("Custom Purchase Invoice"),
            "fieldtype": "Link",
            "options": "Purchase Invoice"
        },
        {
            "fieldname": "expense_account",
            "label": _("Expense Account"),
            "fieldtype": "Link",
            "options": "Account"
        }
    ]


def execute(filters=None):
    columns = [
        _("Name") + ":Link/Landed Cost Voucher:169",
        _("Docstatus") + "::100",
        _("Item Code") + "::120",
        _("Applicable Charges") + "::140",
        _("Custom Item Code") + "::160",
        _("Amount") + "::120",
        _("Account Currency") + "::140",
        _("Description") + "::180",
        _("Custom Purchase Invoice") + "::180",
        _("Expense Account") + "::180",
    ]

    conditions = "1=1"  # A true condition to start building the WHERE clause

    if filters.get("item_code"):
        conditions += " AND lci.item_code = %(item_code)s"
    if filters.get("docstatus"):
        conditions += " AND lcv.docstatus = %(docstatus)s"
    if filters.get("project"):
        conditions += " AND lci.custom_project = %(project)s"
    if filters.get("custom_item_code"):
        conditions += " AND lctc.custom_item_code = %(custom_item_code)s"
    if filters.get("amount"):
        conditions += " AND lctc.amount = %(amount)s"
    if filters.get("account_currency"):
        conditions += " AND lctc.account_currency = %(account_currency)s"
    if filters.get("description"):
        conditions += " AND lctc.description = %(description)s"
    if filters.get("custom_purchase_invoice"):
        conditions += " AND lctc.custom_purchase_invoice = %(custom_purchase_invoice)s"
    if filters.get("expense_account"):
        conditions += " AND lctc.expense_account = %(expense_account)s"

    data = frappe.db.sql(f"""
        SELECT
            lcv.name, lcv.docstatus, lci.item_code, lci.applicable_charges,
            lctc.custom_item_code, lctc.amount, lctc.account_currency, lctc.description,
            lctc.custom_purchase_invoice, lctc.expense_account
        FROM
            `tabLanded Cost Voucher` lcv
        JOIN
            `tabLanded Cost Taxes and Charges` lctc ON lcv.name = lctc.parent
        JOIN
            `tabLanded Cost Item` lci ON lcv.name = lci.parent
        WHERE
            lcv.posting_date BETWEEN %(from_date)s AND %(to_date)s
        
            AND ({conditions} OR {conditions} IS NULL)
        """, {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "docstatus": filters.get("docstatus"),
        "item_code": filters.get("item_code"),
        "project": filters.get("project"),
        "custom_item_code": filters.get("custom_item_code"),
        "amount": filters.get("amount"),
        "account_currency": filters.get("account_currency"),
        "description": filters.get("description"),
        "custom_purchase_invoice": filters.get("custom_purchase_invoice"),
        "expense_account": filters.get("expense_account")
    })

    return columns, data
