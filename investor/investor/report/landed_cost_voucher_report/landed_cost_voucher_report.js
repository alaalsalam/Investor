// Copyright (c) 2023, alaalsalam and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Landed Cost Voucher Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "docstatus",
			"label": __("docstatus"),
			"fieldtype": "Select",
			"options": "\n0\n1\n2",
			"default": "Submitted"
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project"
		},
		{
			"fieldname": "custom_item_code",
			"label": __("Custom Item Code"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "amount",
			"label": __("Amount"),
			"fieldtype": "Currency"
		},
		{
			"fieldname": "account_currency",
			"label": __("Account Currency"),
			"fieldtype": "Link",
			"options": "Currency"
		},
		{
			"fieldname": "description",
			"label": __("Description"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "custom_purchase_invoice",
			"label": __("Custom Purchase Invoice"),
			"fieldtype": "Link",
			"options": "Purchase Invoice"
		},
		{
			"fieldname": "expense_account",
			"label": __("Expense Account"),
			"fieldtype": "Link",
			"options": "Account"
		}
	]
};