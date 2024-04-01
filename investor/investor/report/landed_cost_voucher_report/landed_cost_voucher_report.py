# Copyright (c) 2023, alaalsalam and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Name"), "fieldname": "name", "fieldtype": "Link", "options": "Landed Cost Voucher", "width": 169},
        {"label": _("Docstatus"), "fieldname": "docstatus", "fieldtype": "Data", "width": 100},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Data", "width": 120},
        {"label": _("Applicable Charges"), "fieldname": "applicable_charges", "fieldtype": "Data", "width": 140},
        {"label": _("Custom Item Code"), "fieldname": "custom_item_code", "fieldtype": "Data", "width": 160},
        {"label": _("Amount(USD)"), "fieldname": "base_amount", "fieldtype": "Float", "width": 120},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Float", "width": 120},
        {"label": _("Account Currency"), "fieldname": "account_currency", "fieldtype": "Data", "width": 140},
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 180},
        {"label": _("Custom Purchase Invoice"), "fieldname": "custom_purchase_invoice", "fieldtype": "Data", "width": 180},
        {"label": _("Expense Account"), "fieldname": "expense_account", "fieldtype": "Data", "width": 180}
    ]

    conditions = []
    values = {}

    if filters.get("item_code"):
        conditions.append("lci.item_code = %(item_code)s")
        values["item_code"] = filters.get("item_code")
    if filters.get("docstatus"):
        conditions.append("lcv.docstatus = %(docstatus)s")
        values["docstatus"] = filters.get("docstatus")
    if filters.get("project"):
        conditions.append("lci.custom_project = %(project)s")
        values["project"] = filters.get("project")
    if filters.get("custom_item_code"):
        conditions.append("lci.custom_item_code = %(custom_item_code)s")
        values["custom_item_code"] = filters.get("custom_item_code")
    if filters.get("amount"):
        conditions.append("lci.amount = %(amount)s")
        values["amount"] = filters.get("amount")
    if filters.get("account_currency"):
        conditions.append("lci.account_currency = %(account_currency)s")
        values["account_currency"] = filters.get("account_currency")
    if filters.get("description"):
        conditions.append("lci.description = %(description)s")
        values["description"] = filters.get("description")
    if filters.get("custom_purchase_invoice"):
        conditions.append("lci.custom_purchase_invoice = %(custom_purchase_invoice)s")
        values["custom_purchase_invoice"] = filters.get("custom_purchase_invoice")
    if filters.get("expense_account"):
        conditions.append("lci.expense_account = %(expense_account)s")
        values["expense_account"] = filters.get("expense_account")

    values["applicable_charges"] = filters.get("applicable_charges")

    conditions_query = " AND ".join(conditions)
    conditions_query = f"WHERE {conditions_query}" if conditions_query else ""

    data = frappe.db.sql(f"""
    SELECT
        lcv.name, lcv.docstatus, lci.item_code,
        CASE 
            WHEN COUNT(lctc.name) = 1 THEN 
                CASE
                    WHEN lci.applicable_charges = %(applicable_charges)s THEN -lctc.amount
                    ELSE lci.applicable_charges
                END
            ELSE
                CASE
                    WHEN lci.applicable_charges = %(applicable_charges)s THEN -lctc.amount
                    ELSE lctc.amount
                END
        END AS applicable_charges,
        
        lctc.custom_item_code, lctc.base_amount, lctc.amount, lctc.account_currency,
        lctc.description, lctc.custom_purchase_invoice, lctc.expense_account
    FROM
        `tabLanded Cost Voucher` lcv
    JOIN
        `tabLanded Cost Taxes and Charges` lctc ON lcv.name = lctc.parent
    JOIN
        `tabLanded Cost Item` lci ON lcv.name = lci.parent
    {conditions_query}
    GROUP BY
       lcv.name
    ORDER BY
        lcv.name
""", values,as_dict=True)

    return columns, data