// Copyright (c) 2023, ziad and contributors
// For license information, please see license.txt

frappe.ui.form.on('Landed Cost Voucher', {

    custom_mode_of_payment(frm){
     // console.log(frm.doc);
        if (frm.doc.custom_mode_of_payment) {            
            frappe.call({
                method: "investor.investor.doctype.expense_entry.expense_entry.get_payment_account",
                args: {
                    "mode_of_payment": frm.doc.custom_mode_of_payment,
                    "company": frm.doc.company
                },
                callback: function (r) {
                    if (r.message) {
                        cur_frm.set_value("custom_payment_account", r.message.account);
                        frm.refresh_fields();
                        cur_frm.refresh_field('custom_payment_account');
                    } else {
                        console.log("yyyyyyyy")
                        frm.set_value("custom_payment_account", "");
                        // frm.set_value("party", "");
                        frm.refresh_fields();
                        return;
                    }
                }
            });
            console.log(frm.doc.payment_account)
        }
    },
    // validate(frm){
    //  frm.events.check_items_warehouse();
    // },
    //  get_items_from_purchase_receipts_new(frm) {
    //      console.log("zizo")
    //      // var me = this;
    //      if(!cur_frm.doc.purchase_receipts.length) {
    //          frappe.msgprint(__("Please enter Purchase Receipt first"));
    //      } else {
    //          return frappe.call({
    //                  method: "get_items_from_purchase_receipts_new",
    //                  doc: cur_frm.doc,
    //                  // method: "investor.overrides.landed_cost_voucher.landed_cost_voucher_custom.get_items_from_purchase_receipts_new",
    //                  callback: function(r) {
    //                      // console.log(r);
    //                      cur_frm.events.set_applicable_charges_for_item_new();
    //                  }
    //              });
    //      }
    //  },
    //  set_applicable_charges_for_item_new() {
    //      // var me = this;
    //      if(cur_frm.doc.taxes.length) {
    //          var total_item_cost = 0.0;
    //          var based_on = cur_frm.doc.distribute_charges_based_on.toLowerCase();
 
    //          if (based_on != 'distribute manually') {
    //              $.each(cur_frm.doc.items || [], function(i, d) {
    //                  total_item_cost += flt(d[based_on])
    //              });
 
    //              var total_charges = 0.0;
    //              $.each(cur_frm.doc.items || [], function(i, item) {
    //                  item.applicable_charges = flt(item[based_on]) * flt(cur_frm.doc.total_taxes_and_charges) / flt(total_item_cost)
    //                  item.applicable_charges = flt(item.applicable_charges, precision("applicable_charges", item))
    //                  total_charges += item.applicable_charges
    //              });
 
    //              if (total_charges != cur_frm.doc.total_taxes_and_charges){
    //                  var diff = cur_frm.doc.total_taxes_and_charges - flt(total_charges)
    //                  cur_frm.doc.items.slice(-1)[0].applicable_charges += diff
    //              }
    //              refresh_field("items");
    //              cur_frm.events.check_items_warehouse();
    //          }
    //      }
    //  },
    //   check_items_warehouse: function(){
    //      var warnings = [];
    //      cur_frm.doc.items.forEach( async item => {
    //          var row_data = {
    //              "item_code": item.item_code,
    //              "warehouse": item.warehouse,
    //              "posting_date": cur_frm.doc.posting_date,
    //              "posting_time": frappe.datetime.now_time()
    //          }
    //          var res = await get_actual_qty(row_data);
    //          var actual_qty = 0;
    //          // res = res.json();
    //          // console.log(typeof res)
    //          // console.log(res)
    //          if('qty_after_transaction' in res.message){
    //              console.log("qty_after_transaction found")
    //              actual_qty =  res.message.qty_after_transaction;
    //          }
    //          if(actual_qty < item.qty)
    //              warnings.push({
    //                  "idx": item.idx,
    //                  "item": item.item_code,
    //                  "wh": item.warehouse,
    //                  "qty": item.qty
    //              })
             
    //          if(warnings.length){
    //              let msg = "";
    //              warnings.forEach(w => {
    //                  msg += `Row: <b>${w.idx}</b><br>Item: <b>${w.item}</b> Qty: <b>${w.qty}</b> is less than Qty at Wearhouse: <b>${w.wh}</b><hr><br> `
    //              })
    //              // frappe.msgprint("zizo2")
    //              frappe.throw(msg);
    //          }
 
    //          // console.log(res + "resss")
    //      });
    //  },
     
 
 
 });
 
 async function get_actual_qty(data){
     var r = await frappe.call({
         method: "investor.api.get_actual_qty",
         args: {
             data_dic:data
         }
     });
     return r
 }
 
 
 frappe.ui.form.on('Landed Cost Item', {
 
     items_add: function(frm, cdt, cdn) {
         var child = locals[cdt][cdn];
         var i = child.idx;
         // get actual_qty 
         var row_data = {
             "item_code": d.item_code,
             "warehouse": d.warehouse,
             "posting_date": cur_frm.doc.posting_date,
             "posting_time": frappe.datetime.now_time()
         }
         frappe.call({
             method: "investor.api.get_actual_qty",
             args: {
                 data_dic:""
             },
             callback: function(r) {
                 console.log(r)
             }
         });
 
 
 
     //     // if(child.actual_qty == 0){
     //     //     cur_frm.get_field("items").grid.grid_rows[i].remove();
     //     // }
 
         
     },
 });