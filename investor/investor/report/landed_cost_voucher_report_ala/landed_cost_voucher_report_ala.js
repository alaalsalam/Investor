frappe.query_reports["Landed Cost Voucher Report Ala"] = {
	filters: [
	  {
		fieldname: "from_date",
		label: __("From Date"),
		fieldtype: "Date",
		default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		reqd: 1
	  },
	  {
		fieldname: "to_date",
		label: __("To Date"),
		fieldtype: "Date",
		default: frappe.datetime.get_today(),
		reqd: 1
	  },
	  {
		fieldname: "docstatus",
		label: __("Status"),
		fieldtype: "Select",
		options: "\nDraft\nSubmitted\nCancelled",
		default: "Submitted"
	  },
	  {
		fieldname: "item_code",
		label: __("Item Code"),
		fieldtype: "Link",
		options: "Item"
	  },
	  {
		fieldname: "custom_project",
		label: __("Project"),
		fieldtype: "Link",
		options: "Project"
	  },
	  {
		fieldname: "custom_item_code",
		label: __("Custom Item Code"),
		fieldtype: "Data"
	  },
	  {
		fieldname: "amount",
		label: __("Amount"),
		fieldtype: "Currency"
	  },
	  {
		fieldname: "account_currency",
		label: __("Account Currency"),
		fieldtype: "Link",
		options: "Currency"
	  },
	  {
		fieldname: "description",
		label: __("Description"),
		fieldtype: "Data"
	  },
	  {
		fieldname: "custom_purchase_invoice",
		label: __("Custom Purchase Invoice"),
		fieldtype: "Link",
		options: "Purchase Invoice"
	  },
	  {
		fieldname: "expense_account",
		label: __("Expense Account"),
		fieldtype: "Link",
		options: "Account"
	  },
	  {
		fieldname: "document_type",
		label: __("Document Type"),
		fieldtype: "Select",
		options: "\nLanded Cost Voucher\nStock Entry",
		default: "Type 1"
	  }
	]
  };