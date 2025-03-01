// Copyright (c) 2023, ziad and contributors
// For license information, please see license.txt
// لاFor license information, please see license.txt

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
	refresh: function (frm) {
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(
				__("Project"),
				function () {
					const dialog = new frappe.ui.form.MultiSelectDialog({
						doctype: "Project",
						target: frm,
						setters: [
							{
								label: "Total Available for Funding Other Deals",
								fieldname: "custom_total_available_for_funding_other_deals",
								fieldtype: "Currency",
							},
							{
								label: "Start Date",
								fieldname: "custom_start_date",
								fieldtype: "Date",
							},
						],
						add_filters_group: 1,
						get_query() {
							return {
								custom_total_available_for_funding_other_deals: frm.doc.custom_total_available_for_funding_other_deals || undefined,
								custom_start_date: frm.doc.custom_start_date || undefined,
							};
						},
						action(selections) {
							if (selections.length > 0) {
								let funding_dialog = new frappe.ui.Dialog({
									title: __("Enter Investment Amounts"),
									fields: selections.map(project_name => ({
										label: __("Investment Amount for {0}", [project_name]),
										fieldname: project_name,
										fieldtype: "Currency",
										reqd: 1
									})),
									primary_action_label: __("Confirm"),
									primary_action(values) {
										frappe.db.get_value('Investor Settings', null, ['investor_group', 'investor_account'])
											.then(setting => {
												const investor_group = setting.message.investor_group;
												const investor_account = setting.message.investor_account;
	
												selections.forEach(project_name => {
													const investment_amount = values[project_name] || 0;
	
													frappe.db.exists('Investor', project_name).then(exists => {
														if (exists) {
															frappe.show_alert({
																message: __("Investor {0} already exists. Skipping creation.", [project_name]),
																indicator: 'orange'
															});
	
															createInvestorContract(project_name, investor_account, investment_amount, frm);
														} else {
															frappe.call({
																method: "frappe.client.insert",
																args: {
																	doc: {
																		doctype: "Investor",
																		investor_name: project_name,
																		investor_group: investor_group,
																		status: "Active",
																	}
																},
																callback: function (r) {
																	if (r.message) {
																		frappe.show_alert({
																			message: __("Investor {0} created successfully.", [project_name]),
																			indicator: 'green'
																		});
	
																		createInvestorContract(project_name, investor_account, investment_amount, frm);
																	}
																}
															});
														}
													});
	
												});
	
												funding_dialog.hide();
											});
									}
								});
	
								funding_dialog.show();
								dialog.dialog.hide();
							} else {
								frappe.msgprint(__('Please select at least one project.'));
							}
						}
					});
				}
			);
		}
	}
	
	
	
	
 });

function createInvestorContract(party_name, investor_account, investment_amount, frm) {
    frappe.call({
        method: "frappe.client.insert",
        args: {
            doc: {
                doctype: "investor Contract",
                party_name: party_name,
                posting_date: frappe.datetime.get_today(),
                investor_account: investor_account,
                contract_terms: party_name,
                contract_type: "Sub Contract",
                investment_amount: investment_amount,
                docstatus: 0 
            }
        },
        callback: function (r) {
            if (r.message) {
                let contract_name = r.message.name;

                frappe.call({
                    method: "frappe.client.submit",
                    args: {
                        doc: r.message
                    },
                    callback: function (submit_res) {
                        if (submit_res.message) {
                            frappe.show_alert({
                                message: __("Contract created for {0} with amount {1}", [party_name, investment_amount]),
                                indicator: 'green'
                            });

                            let child = frm.add_child("custom_investment_contracts");
                            let cdt = child.doctype;
                            let cdn = child.name;

                            frappe.model.set_value(cdt, cdn, "investor_contract", contract_name);
                            frappe.model.set_value(cdt, cdn, "investor_name", party_name);
                            frappe.model.set_value(cdt, cdn, "investment_amount", investment_amount);

                            frm.refresh_field("custom_investment_contracts");
                            updateProjectFunding(party_name, investment_amount);
                        }
                    }
                });
            }
        }
    });
}

function updateProjectFunding(project_name, investment_amount) {
    frappe.db.get_value("Project", project_name, "custom_total_available_for_use_in_deal")
        .then(project => {
            let current_value = project.message.custom_total_available_for_use_in_deal || 0;
            let new_value = current_value + investment_amount;

            frappe.db.set_value("Project", project_name, "custom_total_available_for_use_in_deal", new_value)
                .then(() => {
                    frappe.show_alert({
                        message: __("Updated available funding for {0} to {1}", [project_name, new_value]),
                        indicator: 'blue'
                    });
                });
        });
}