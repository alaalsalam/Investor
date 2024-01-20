// Copyright (c) 2023, alaalsalam and contributors
// For license information, please see license.txt

frappe.ui.form.on('investor Contract', {
	refresh: function (frm){
		frm.events.show_general_ledger(frm);
		// set_account_currency_and_balance(frm, frm.doc.payment_account)


	},
	show_general_ledger: function(frm) {
		if(frm.doc.docstatus == 1 || 1) {
			frm.add_custom_button(__('Ledger'), function() {
				frappe.route_options = {
					"voucher_no": frm.doc.name,
					"from_date": frm.doc.start_date,
					"to_date": moment(frm.doc.modified).format('YYYY-MM-DD'),
					"company": frm.doc.company,
					"group_by": "",
					"show_cancelled_entries": frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "General Ledger");
			}, "fa fa-table");
		}
	},

	set_account_currency_and_balance: function(frm) {
		if (frm.doc.start_date && profit_and_loss_account_to_project) {
			frappe.call({	
				method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_account_details",
				args: {
					"account": account,
					"date": frm.doc.posting_date,
					"cost_center": frm.doc.cost_center,
					"project": frm.doc.project,
				},
				callback: function(r, ) {
					if(r.message) {
						console.log("----------->",r.message)
						// frappe.run_serially([
						// 	() => frm.set_value('account_currency', r.message['account_currency']),
						// 	() => {
						// 		frm.set_value('payment_account_balance', r.message['account_balance']);
						// 	}
						// ]);
					}
				}
			});
		}
	},
	contract_template: function (frm) {
		if (frm.doc.contract_template) {
			frappe.call({
				method: 'erpnext.crm.doctype.contract_template.contract_template.get_contract_template',
				args: {
					template_name: frm.doc.contract_template,
					doc: frm.doc
				},
				callback: function(r) {
					if (r && r.message) {
						let contract_template = r.message.contract_template;
						frm.set_value("contract_terms", r.message.contract_terms);
						frm.set_value("requires_fulfilment", contract_template.requires_fulfilment);

						if (frm.doc.requires_fulfilment) {
							// Populate the fulfilment terms table from a contract template, if any
							r.message.contract_template.fulfilment_terms.forEach(element => {
								let d = frm.add_child("fulfilment_terms");
								d.requirement = element.requirement;
							});
							frm.refresh_field("fulfilment_terms");
						}
					}
				}
			});
		}
	},
});
