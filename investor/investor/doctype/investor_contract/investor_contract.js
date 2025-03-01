// // Copyright (c) 2023, alaalsalam and contributors
// // For license information, please see license.txt


frappe.ui.form.on('investor Contract', {
    
	refresh: function (frm){
       
       
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(
                __("Investor Contract"),
                function () {
                    const dialog = new frappe.ui.form.MultiSelectDialog({
                        doctype: "investor Contract",
                        target: frm,
                        setters: [
                            {
                                label: "Project",
                                fieldname: "project",
                                fieldtype: "Link",
                                options: "Project",  
                            },
                            {
                                label: "party_name",
                                fieldname: "party_name",
                                fieldtype: "Link",
                                options: "Investor", 
                            },
                            {
                                label: "Funding Available",
                                fieldname: "funding_available",
                                fieldtype: "Float", 
                            },
                        ],
                        add_filters_group: 1,
                        date_field: "party_name",
                        get_query() {
                            return {
                                project: frm.doc.project || undefined,
                                party_name: frm.doc.party_name || undefined,
                            };
                        },
                        action(selections) {
                            if (selections.length > 0) {
                                const source_name = selections[0]; 
                                
                                frappe.call({
                                    method: "investor.utils.map_investor_contract",
                                    args: {
                                        source_name: source_name
                                    },
                                    callback: function (r) {
                                        if (r.message) {
                                            const new_contract = r.message; 
                                            
                                            frm.set_value("party_name", new_contract.party_name);
                                            frm.set_value("investment_amount", new_contract.funding_available);
                                            frm.set_value("project", new_contract.project);
                                            frm.set_value("project_name", new_contract.project_name);
                                            frm.set_value("posting_date", frappe.datetime.get_today());
                                            dialog.dialog.hide();                                    //         frappe.msgprint(__('Investor Contract successfully mapped.'));
                                    //         frappe.msgprint(__('Mapped Contract: ') + 
                                    //             '\nParty Name: ' + new_contract.party_name +
                                    //             '\nFunding Available: ' + new_contract.funding_available +
                                    //             '\nProject: ' + new_contract.project);
                                            
                                    //         console.log("Mapped Investor Contract Data:", new_contract);
                                        } 
                                    // else {
                                    //         frappe.msgprint(__('Error mapping the contract.'));
                                    //     }
                                    }
                                });
                            } else {
                                frappe.msgprint(__('Please select an investor contract.'));
                            }
                        }
                    });
                }
            );
        }
        if (frm.doc.docstatus === 1 && frm.doc.status === "Fulfilled") {
		frm.events.show_general_ledger(frm);}
		frm.add_custom_button(__('Payment Entry'), function () {
			frappe.call({
				method: "investor.utils.make_payment_entry",
				args: {
					source_name: frm.doc.name
				},
				callback: function (r) {
					if (r.message) {
						frappe.model.sync(r.message);
						frappe.set_route("Form", r.message.doctype, r.message.name);
					}
				}
			});
		}, __('Create'));
      
		// set_account_currency_and_balance(frm, frm.doc.payment_account)


	},
	party_name: function (frm) {
        

        frappe.call({
            method: "erpnext.accounts.party.get_party_account",
            args: {
                party_type: "Investor",
                party: frm.doc.party_name,
                company: frm.doc.company,
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value("investor_account", r.message);
                    console.log("Investor Account:", r.message);
                } else {
                    frappe.msgprint(__("No account found for the selected Investor."));
                }
            },
        });
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
function extract_and_store_dividends(frm) {
    const terms_text = frm.doc.contract_terms;

   
        const percentages = terms_text.match(/\d+(\.\d+)?%/g);

        if (percentages) {
            percentages.forEach((percentage) => {
                const value = parseFloat(percentage.replace('%', ''));

                const child = frm.add_child('contract_dividend_ratios');
                child.dividend = value; 
            });

            frm.refresh_field('contract_dividend_ratios');
        }
    
}


;
frappe.ui.form.on('Contract Dividend Ratios', {
    // party_name: function (frm, cdt, cdn) {
    //     let row = locals[cdt][cdn]; 
    //     if (!row.party_name) {
    //         frappe.msgprint(__("Please select a Party Name."));
    //         return;
    //     }

    //     frappe.call({
    //         method: "erpnext.accounts.party.get_party_account", // دالة Python لجلب الحساب
    //         args: {
    //             party_type: "Investor", 
    //             party: row.party_name,
    //             company: frm.doc.company, 
    //         },
    //         callback: function (r) {
    //             if (r.message) {
    //                 frappe.model.set_value(cdt, cdn, "account", r.message); // تعيين الحساب في الحقل "account"
    //                 console.log("Account for Party:", r.message);
    //             } 
    //         },
    //     });
    // },
	party_name: function (frm, cdt, cdn) {
        handle_party_logic(frm, cdt, cdn);
    },
    party_type: function (frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.party_name) {
            handle_party_logic(frm, cdt, cdn);
        }
    }
});

function handle_party_logic(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);

    if (!row.party_type) {
        frappe.msgprint(__('Please select a Party Type.'));
        return;
    }

    switch (row.party_type) {
        case 'Company':
            frappe.db.get_single_value('Investor Settings', 'company_account')
                .then(value => {
                    if (value) {
                        frappe.model.set_value(cdt, cdn, 'account', value);
                    } else {
                        frappe.msgprint(__('No company account found in Investor Settings.'));
                    }
                });
            break;

        case 'Investor':
            if (!row.party_name) {
                frappe.msgprint(__('Please select a Party Name.'));
                return;
            }
            frappe.call({
                method: 'erpnext.accounts.party.get_party_account',
                args: {
                    party_type: 'Investor',
                    party: row.party_name,
                    company: frm.doc.company,
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'account', r.message);
                        console.log('Account for Party:', r.message);
                    }
                },
            });
            break;

        case 'Account':
            frappe.model.set_value(cdt, cdn, 'account', row.party_name);
            break;

        default:
            frappe.msgprint(__('Invalid Party Type.'));
    }

    frm.refresh_field('child_table_fieldname');
}