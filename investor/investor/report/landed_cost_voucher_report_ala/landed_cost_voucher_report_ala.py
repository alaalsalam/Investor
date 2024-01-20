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
            "label": _("Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nSubmitted\nCancelled",
            "default": "1"  # Set the default value to "Submitted"
        },
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Item"
        },
        {
            "fieldname": "custom_project",
            "label": _("Custom Project"),
            "fieldtype": "Link",
            "options": "Custom Project"
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
        {
            "fieldname": "name",
            "label": _("Name"),
            "fieldtype": "Dynamic Link",
            "options": "document_type",
            "width": 169
        },
       
        {
            "fieldname": "document_type",
            "label": _("Document Type"),
            "fieldtype": "Select",
            "options": "Document Type",
            "width": 120
        },
       
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "options": "Status",
            "width": 40
        },
        _("Item Code") + "::170",
        _("Applicable Charges") + "::140",
        _("Custom Item Code") + "::160",
        _("Amount") + "::120",
        _("Account Currency") + "::140",
        _("Description") + "::180",
        _("Custom Purchase Invoice") + "::180",
        _("Expense Account") + "::180",
    ]

    conditions = "1=1"  # A true condition to start building the WHERE clause
    conditions_stock = "1=1"  # A true condition to start building the WHERE clause

    if filters.get("docstatus"):
        docstatus_map = {
            "Draft": 0,
            "Submitted": 1,
            "Cancelled": 2
        }
        docstatus_value = docstatus_map.get(filters["docstatus"])
        conditions += " AND lcv.docstatus = %(docstatus)s"
        conditions_stock += " AND se.docstatus = %(docstatus)s"
        filters["docstatus"] = docstatus_value

    if filters.get("item_code"):
        conditions += " AND lci.item_code = %(item_code)s"
        conditions_stock += " AND lci.item_code = %(item_code)s"
    if filters.get("custom_project"):
        conditions += " AND lci.custom_project = %(custom_project)s"
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
        conditions_stock += " AND lctc.custom_purchase_invoice = %(custom_purchase_invoice)s"
    if filters.get("expense_account"):
        conditions += " AND lctc.expense_account = %(expense_account)s"
        conditions_stock += " AND lctc.expense_account = %(expense_account)s"
    if filters.get("document_type"):
        conditions += " AND se.doctype = %(document_type)s"
        conditions_stock += " AND se.doctype = %(document_type)s"

    data = frappe.db.sql("""
        SELECT
            lcv.name, lcv.doctype, lcv.docstatus, lci.item_code, lci.applicable_charges,
            lctc.custom_item_code, lctc.amount, lctc.account_currency, lctc.description,
            lctc.custom_purchase_invoice, lctc.expense_account, null
        FROM
            `tabLanded Cost Voucher` lcv
        LEFT JOIN
            `tabLanded Cost Taxes and Charges` lctc ON lcv.name = lctc.parent
        LEFT JOIN
            `tabLanded Cost Item` lci ON lcv.name = lci.parent
        WHERE
            lcv.posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND ({conditions})

        UNION

        SELECT
            se.name, se.doctype, se.docstatus, sed.item_code, sed.additional_cost,
            lctc.custom_item_code, lctc.amount, lctc.account_currency, lctc.description,
            lctc.custom_purchase_invoice, lctc.expense_account, null
        FROM
            `tabStock Entry` se
        LEFT JOIN
            `tabLanded Cost Taxes and Charges` lctc ON se.name = lctc.parent
        LEFT JOIN
            `tabStock Entry Detail` sed ON se.name = sed.parent
        WHERE
            se.posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND ({conditions_stock})
        """.format(conditions=conditions,conditions_stock=conditions_stock), filters)

    return columns, data

   
# def execute(filters=None):
#     columns = [
#         _("Name") + ":Link/Landed Cost Voucher:169",
#         _("Status") + "::40",
#         _("Item Code") + "::160",
#         _("Applicable Charges") + "::140",
#         _("Custom Item Code") + "::160",
#         _("Amount") + "::120",
#         _("Account Currency") + "::140",
#         _("Description") + "::180",
#         _("Custom Purchase Invoice") + "::180",
#         _("Expense Account") + "::180",
#     ]

#     conditions = "1=1"  # A true condition to start building the WHERE clause

#     if filters.get("docstatus"):
#         docstatus_map = {
#             "Draft": 0,
#             "Submitted": 1,
#             "Cancelled": 2
#         }
#         docstatus_value = docstatus_map.get(filters["docstatus"])
#         conditions += " AND lcv.docstatus = %(docstatus)s"
#         filters["docstatus"] = docstatus_value

#     if filters.get("item_code"):
#         conditions += " AND lci.item_code = %(item_code)s"
#     if filters.get("custom_project"):
#         conditions += " AND lci.custom_project = %(custom_project)s"
#     if filters.get("custom_item_code"):
#         conditions += " AND lctc.custom_item_code = %(custom_item_code)s"
#     if filters.get("amount"):
#         conditions += " AND lctc.amount = %(amount)s"
#     if filters.get("account_currency"):
#         conditions += " AND lctc.account_currency = %(account_currency)s"
#     if filters.get("description"):
#         conditions += " AND lctc.description = %(description)s"
#     if filters.get("custom_purchase_invoice"):
#         conditions += " AND lctc.custom_purchase_invoice = %(custom_purchase_invoice)s"
#     if filters.get("expense_account"):
#         conditions += " AND lctc.expense_account = %(expense_account)s"

#     data = frappe.db.sql("""
#         SELECT
#             lcv.name, lcv.docstatus, lci.item_code, lci.applicable_charges,
#             lctc.custom_item_code, lctc.amount, lctc.account_currency, lctc.description,
#             lctc.custom_purchase_invoice, lctc.expense_account
#         FROM
#             `tabLanded Cost Voucher` lcv
#         LEFT JOIN
#             `tabLanded Cost Taxes and Charges` lctc ON lcv.name = lctc.parent
#         LEFT JOIN
#             `tabLanded Cost Item` lci ON lcv.name = lci.parent
#         WHERE
#             lcv.posting_date BETWEEN %(from_date)s AND %(to_date)s
#             AND ({conditions})
#         """.format(conditions=conditions), filters)

#     return columns, data
