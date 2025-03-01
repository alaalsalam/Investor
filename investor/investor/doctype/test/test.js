// // Copyright (c) 2025, alaalsalam and contributors
// // For license information, please see license.txt

frappe.ui.form.on("test", {
	refresh(frm) {
        const crm_notes = new erpnext.utils.CRMNotes({
			frm: this.frm,
			notes_wrapper: $(this.frm.fields_dict.notes_html.wrapper),
		});
		crm_notes.refresh();
	},
});

//   // تعريف الـ Dialog
// // تعريف الـ Dialog
// let savedLogs = []; // مصفوفة لحفظ القيم المدخلة سابقاً

// // تعريف الـ Dialog
// const dialog = new frappe.ui.Dialog({
//   title: __("Create Logs"),
//   fields: [
//     {
//       fieldname: "logs",
//       fieldtype: "Table",
//       label: __("Logs"),
//       in_place_edit: true,
//       reqd: 1,
//       fields: [
//         {
//           fieldname: "log_type",
//           label: __("Log Type"),
//           fieldtype: "Select",
//           options: "\nIN\nOUT",
//           in_list_view: 1,
//           reqd: 1,
//         },
//         {
//           fieldname: "time",
//           label: __("Time"),
//           fieldtype: "Time",
//           in_list_view: 1,
//           reqd: 1,
//         },
//       ],
//       on_add_row: (idx) => {
//         // تعديل نوع السجل بناءً على الفهرس
//         let data_id = idx - 1;
//         let logs = dialog.fields_dict.logs;
//         let log_type = (data_id % 2) === 0 ? "IN" : "OUT";

//         logs.df.data[data_id].log_type = log_type;
//         logs.grid.refresh();
//       },
//     },
//   ],
//   primary_action: (values) => {
//     // حفظ القيم عند الضغط على الزر الأساسي
//     savedLogs = values.logs; // حفظ القيم المدخلة
//     frappe.msgprint({
//       title: __("Success"),
//       message: __("Logs have been saved successfully."),
//       indicator: "green",
//     });
//     dialog.hide();
//   },
//   primary_action_label: __("Create"),
// });

// // وظيفة لفتح الـ Dialog وتحميل القيم المحفوظة
// function openDialog() {
//   if (savedLogs.length > 0) {
//     // إذا كانت هناك قيم محفوظة، يتم تحميلها في الجدول
//     dialog.fields_dict.logs.df.data = savedLogs;
//     dialog.fields_dict.logs.grid.refresh();
//   }
//   dialog.show();
// }

// // دمج الزر داخل نموذج Doctype
// frappe.ui.form.on('Test', {
//   refresh: function(frm) {
//     // إضافة زر "Show" إلى النموذج
//     frm.add_custom_button('Show', function() {
//       openDialog();
//       dialog.show(); // فتح الحوار عند الضغط على الزر
//     });
//   },
//   show: function(frm) {
//     // إضافة زر "Show" إلى النموذج
    
//     dialog.show();  // فتح الحوار عند الضغط على الزر
    
//   },
// });
// frappe.ui.form.on('Contract Dividend Ratios', {
//   refresh: function (frm) {
//       frm.fields_dict['contract_dividend_ratios'].grid.add_custom_button(__('show'), function () {
//           // استدعاء الدالة لإنشاء الحوار
//           create_dialog_with_table(frm);
//       });
//   },
//   show: function (frm) {
//     open_cost_dialog(frm,cdt, cdn);
//   }
// });
// function open_cost_table_dialog(frm) {
//   const dialog = new frappe.ui.Dialog({
//       title: __('Cost Table'),
//       size: 'large',
//       fields: [
//           {
//               fieldname: 'entries',
//               fieldtype: 'Table',
//               label: __('Cost Details'),
//               cannot_add_rows: false,
//               in_place_edit: true,
//               data: frm.doc.cost_table || [],  // تحميل البيانات الحالية
//               fields: [
//                   {
//                       fieldtype: 'Select',
//                       fieldname: 'cost_type',
//                       Option:("راتب","تامين"),
//                       label: __('Cost Type'),
//                       in_list_view: 1
//                   },
//                   {
//                       fieldtype: 'Float',
//                       fieldname: 'amount',
//                       label: __('Amount'),
//                       in_list_view: 1
//                   }
//               ]
//           }
//       ],
//       primary_action_label: __('Save'),
//       primary_action(values) {
//           save_cost_table_entries(frm, values.entries, dialog);
//       }
//   });

//   dialog.show();
// }






// function save_cost_table_entries(frm, entries, dialog) {
//     //   // تحديث الواجهة
//     frm.save().then(() => {
//         frappe.msgprint(__('Cost details have been saved successfully.'));
//         dialog.hide();
//     });
// }


// function open_cost_dialog(frm, cdt, cdn) {
//     const child_row = frappe.get_doc(cdt, cdn); // الصف الحالي في Contract Dividend Ratios

//     const dialog = new frappe.ui.Dialog({
//         title: __('Cost Details'),
//         fields: [
//             {
//                 fieldname: 'cost_entries',
//                 fieldtype: 'Table',
//                 cannot_add_rows: false,
//                 allow_bulk_edit: true,
//                 fields: [
//                     {
//                         fieldtype: 'Select',
//                         fieldname: 'cost_type',
//                         options: ["راتب", "تأمين"],
//                         label: __('Cost Type'),
//                         in_list_view: 1
//                     },
//                     {
//                         fieldtype: 'Float',
//                         fieldname: 'amount',
//                         label: __('Amount'),
//                         in_list_view: 1
//                     }
//                 ]
//             }
//         ],
//         primary_action_label: __('Save'),
//         primary_action(values) {
//             save_cost_table_entries(frm, values.entries, dialog);
//         }
//     });

//     // استرجاع البيانات من Cost Amount إذا كان cost_id موجودًا
//     if (child_row.cost_id) {
//         frappe.db.get_doc('Cost Amount', child_row.cost_id)
//             .then(doc => {
//                 if (doc && doc.cost_table) {
//                     dialog.set_value('cost_entries', doc.cost_table);
//                 }
//                 dialog.show();
//             })
//             .catch(() => {
//                 frappe.msgprint(__('Unable to fetch the Cost Amount document.'));
//                 dialog.show();
//             });
//     } else {
//         dialog.show();
//     }
// }

// function save_cost_data(frm, child_row, entries, dialog) {
//     const cost_doc = {
//         doctype: 'Cost Amount',
//         cost_table: entries
//     };

//     frappe.call({
//         method: child_row.cost_id ? 'frappe.client.save' : 'frappe.client.insert',
//         args: {
//             doc: child_row.cost_id ? { ...cost_doc, name: child_row.cost_id } : cost_doc
//         },
//         callback(response) {
//             const saved_doc = response.message;
//             if (saved_doc) {
//                 // حفظ اسم المستند الجديد في cost_id
//                 frappe.model.set_value(child_row.doctype, child_row.name, 'cost_id', saved_doc.name);
//                 frm.refresh_field('contract_dividend_ratios');
//                 frappe.msgprint(__('Cost data has been successfully saved.'));
//             }
//             dialog.hide();
//         },
//         error: (err) => {
//             frappe.msgprint(__('An error occurred while saving the data.'));
//             console.error(err);
//         }
//     });
// }#ص#############################################
//الاصدار الاخير
// frappe.ui.form.on('Contract Dividend Ratios', {
//     show: function (frm, cdt, cdn) {
//         open_cost_dialog(frm, cdt, cdn); // تمرير cdt و cdn للصف الحالي
//     }
// });

// function open_cost_dialog(frm, cdt, cdn) {
//     const child_row = frappe.get_doc(cdt, cdn);

//     const dialog = new frappe.ui.Dialog({
//         title: __('Cost Details'),
//         fields: [
//             {
//                 fieldname: 'cost_entries',
//                 fieldtype: 'Table',
//                 cannot_add_rows: false,
//                 allow_bulk_edit: true,
//                 fields: [
//                     {
//                         fieldtype: 'Select',
//                         fieldname: 'cost_type',
//                         options: ["راتب", "تامين"],
//                         label: __('Cost Type'),
//                         in_list_view: 1
//                     },
//                     {
//                         fieldtype: 'Float',
//                         fieldname: 'amount',
//                         label: __('Amount'),
//                         in_list_view: 1
//                     }
//                 ]
//             }
//         ],
//         primary_action_label: __('Save'),
//         primary_action(values) {
//             save_cost_data(frm, child_row, values.cost_entries, dialog);
//         }
//     });

//     if (child_row.cost_id) {
//         frappe.call({
//             method: "frappe.client.get",
//             args: { doctype: "Cost Amount", name: child_row.cost_id },
//             callback: function (response) {
//                 const doc = response.message;
//                 if (doc && doc.cost_table) {
//                     set_data_to_dialog(doc.cost_table, dialog);
//                 }
//                 dialog.show();
//             }
//         });
//     } else {
//         dialog.show();
//     }
// }

// function set_data_to_dialog(data, dialog) {
//     const cost_entries_field = dialog.fields_dict.cost_entries;
//     if (!cost_entries_field.df.data) {
//         cost_entries_field.df.data = [];
//     }
//     data.forEach((entry) => {
//         cost_entries_field.df.data.push({
//             cost_type: entry.cost_type || "",
//             amount: entry.amount || 0
//         });
//     });
//     cost_entries_field.grid.refresh();
// }

// function save_cost_data(frm, child_row, entries, dialog) {
//     const cost_doc = {
//         doctype: 'Cost Amount',
//         cost_table: entries
//     };

//     frappe.call({
//         method: child_row.cost_id ? 'frappe.client.save' : 'frappe.client.insert',
//         args: {
//             doc: child_row.cost_id ? { ...cost_doc, name: child_row.cost_id } : cost_doc
//         },
//         callback(response) {
//             const saved_doc = response.message;
//             if (saved_doc) {
//                 frappe.model.set_value(child_row.doctype, child_row.name, 'cost_id', saved_doc.name);
//                 frm.refresh_field('contract_dividend_ratios');
//                 frappe.msgprint(__('Cost data has been successfully saved.'));
//             }
//             dialog.hide();
//         },
//         error: (err) => {
//             frappe.msgprint(__('An error occurred while saving the data.'));
//             console.error(err);
//         }
//     });
// }

frappe.ui.form.on('Contract Dividend Ratios', {
    show: function (frm, cdt, cdn) {
        open_cost_dialog(frm, cdt, cdn); // تمرير cdt و cdn للصف الحالي
    },
   
});
erpnext.utils.CRMNotes = class CRMNotes {
	constructor(opts) {
		$.extend(this, opts);
	}

	refresh() {
		var me = this;
		this.notes_wrapper.find(".notes-section").remove();

		let notes = this.frm.doc.notes || [];
		notes.sort((a, b) => new Date(b.added_on) - new Date(a.added_on));

		let notes_html = frappe.render_template("crm_notes", {
			notes: notes.map(note => ({
				note: note.note,
				custom_item_code: note.custom_item_code || "No Item Code",
				added_on: note.added_on
			})),
		});
		$(notes_html).appendTo(this.notes_wrapper);

		this.add_note();

		$(".notes-section")
			.find(".edit-note-btn")
			.on("click", function () {
				me.edit_note(this);
			});

		$(".notes-section")
			.find(".delete-note-btn")
			.on("click", function () {
				me.delete_note(this);
			});
	}

	add_note() {
		let me = this;
		let _add_note = () => {
			var d = new frappe.ui.Dialog({
				title: __("Add a Note"),
				fields: [
					{
						label: "Item Code",
						fieldname: "custom_item_code",
						fieldtype: "Data",
						reqd: 0
					},
					{
						label: "Note",
						fieldname: "note",
						fieldtype: "Text Editor",
						reqd: 1,
						enable_mentions: true,
					},
				],
				primary_action: function () {
					var data = d.get_values();
					frappe.call({
						method: "frappe.client.insert",
						args: {
							doc: {
								doctype: "CRM Note",
								note: data.note,
								custom_item_code: data.custom_item_code,
								reference_doctype: me.frm.doctype,
								reference_name: me.frm.docname,
							},
						},
						callback: function (r) {
							if (!r.exc) {
								me.frm.refresh_field("notes");
								me.refresh();
							}
							d.hide();
						},
					});
				},
				primary_action_label: __("Add"),
			});
			d.show();
		};
		$(".new-note-btn").click(_add_note);
	}

	edit_note(edit_btn) {
		var me = this;
		let row = $(edit_btn).closest(".comment-content");
		let row_id = row.attr("name");
		let row_content = $(row).find(".content").html();
		let item_code = $(row).find(".custom-item-code").text();

		if (row_content) {
			var d = new frappe.ui.Dialog({
				title: __("Edit Note"),
				fields: [
					{
						label: "Item Code",
						fieldname: "custom_item_code",
						fieldtype: "Data",
						default: item_code,
						reqd: 0
					},
					{
						label: "Note",
						fieldname: "note",
						fieldtype: "Text Editor",
						default: row_content,
					},
				],
				primary_action: function () {
					var data = d.get_values();
					frappe.call({
						method: "frappe.client.set_value",
						args: {
							doctype: "CRM Note",
							name: row_id,
							fieldname: {
								note: data.note,
								custom_item_code: data.custom_item_code
							}
						},
						callback: function (r) {
							if (!r.exc) {
								me.frm.refresh_field("notes");
								me.refresh();
								d.hide();
							}
						},
					});
				},
				primary_action_label: __("Done"),
			});
			d.show();
		}
	}

	delete_note(delete_btn) {
		var me = this;
		let row_id = $(delete_btn).closest(".comment-content").attr("name");
		frappe.call({
			method: "frappe.client.delete",
			args: {
				doctype: "CRM Note",
				name: row_id,
			},
			callback: function (r) {
				if (!r.exc) {
					me.frm.refresh_field("notes");
					me.refresh();
				}
			},
		});
	}
};


function open_cost_dialog(frm, cdt, cdn) {
    const child_row = frappe.get_doc(cdt, cdn);

    const dialog = new frappe.ui.Dialog({
        title: __('Cost Details'),
        fields: [
            {
                fieldname: 'cost_entries',
                fieldtype: 'Table',
                cannot_add_rows: false,
                allow_bulk_edit: true,
                fields: [
                    {
                        fieldtype: 'Select',
                        fieldname: 'cost_type',
                        options: ["راتب", "تامين"],
                        label: __('Cost Type'),
                        in_list_view: 1
                    },
                    {
                        fieldtype: 'Float',
                        fieldname: 'amount',
                        label: __('Amount'),
                        in_list_view: 1
                    }
                ]
            }
        ],
        primary_action_label: __('Save'),
        primary_action(values) {
            save_cost_data(frm, child_row, values.cost_entries, dialog);
        }
    });

    if (child_row.cost_id) {
        frappe.call({
            method: "frappe.client.get",
            args: { doctype: "Cost Amount", name: child_row.cost_id },
            callback: function (response) {
                const doc = response.message;
                if (doc && doc.cost_table) {
                    set_data_to_dialog(doc.cost_table, dialog);
                }
                dialog.show();
            }
        });
    } else {
        dialog.show();
    }
}

function set_data_to_dialog(data, dialog) {
    const cost_entries_field = dialog.fields_dict.cost_entries;
    if (!cost_entries_field.df.data) {
        cost_entries_field.df.data = [];
    }
    data.forEach((entry) => {
        cost_entries_field.df.data.push({
            cost_type: entry.cost_type || "",
            amount: entry.amount || 0
        });
    });
    cost_entries_field.grid.refresh();
}

function save_cost_data(frm, child_row, entries, dialog) {
    const cost_doc = {
        doctype: 'Cost Amount',
        cost_table: entries
    };

    if (child_row.cost_id) {
        // إذا كان لدينا cost_id، نقوم بإنشاء دوك تايب جديد بدلاً من تعديل القديم
        frappe.call({
            method: 'frappe.client.get',
            args: { doctype: 'Cost Amount', name: child_row.cost_id },
            callback: function(response) {
                const doc = response.message;
                if (doc) {
                    // إذا كانت البيانات قد تم تعديلها، ننشئ دوك تايب جديد
                    create_new_cost_doc(frm, child_row, cost_doc, dialog);
                } else {
                    create_new_cost_doc(frm, child_row, cost_doc, dialog);
                }
            },
            error: function(err) {
                frappe.msgprint(__('An error occurred while verifying the document.'));
                console.error(err);
            }
        });
    } else {
        // إذا لم يكن لدينا cost_id، ننشئ دوك تايب جديد مباشرة
        create_new_cost_doc(frm, child_row, cost_doc, dialog);
    }
}

function create_new_cost_doc(frm, child_row, cost_doc, dialog) {
    frappe.call({
        method: 'frappe.client.insert',
        args: {
            doc: cost_doc
        },
        callback(response) {
            const saved_doc = response.message;
            if (saved_doc) {
                // ربط الـ child_row بالـ cost_id الجديد
                frappe.model.set_value(child_row.doctype, child_row.name, 'cost_id', saved_doc.name);

                // تحديث النموذج والجدول الفرعي بعد الحفظ
                frm.refresh_field('contract_dividend_ratios');
                frm.fields_dict['contract_dividend_ratios'].grid.refresh();

                frappe.msgprint(__('Cost data has been successfully saved.'));
            }
            dialog.hide();
        },
        error: (err) => {
            frappe.msgprint(__('An error occurred while saving the data.'));
            console.error(err);
        }
    });
}
