// Copyright (c) 2023, ziad and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project', {
    setup: function(frm) {
		frm.set_query("investor_contract", "custom_investment_contracts", function() {
			return {
				filters: {
					company: frm.doc.company,
					docstatus: 1
				}
			};
		});
		frm.set_query("custom_closing_account_head", function() {
			return {
				filters: [
					['Account', 'company', '=', frm.doc.company],
					['Account', 'is_group', '=', '0'],
					['Account', 'freeze_account', '=', 'No'],
					['Account', 'root_type', 'in', 'Liability, Equity']
				]
			}
		});
	},
 });