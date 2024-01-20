
import frappe
from frappe import _

from erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher import LandedCostVoucher

class LandedCostVoucherCustom(LandedCostVoucher):
	@frappe.whitelist()
	def get_items_from_purchase_receipts_new(self):
		self.set("items", [])
		# if self.get("purchase_receipts"):
		# 	frappe.msgprint(f"no prs{len(self.purchase_receipts)}")
		for pr in self.get("purchase_receipts"):
			if pr.receipt_document_type and pr.receipt_document:
				pr_items = frappe.db.sql(
					"""select 
							pr_item.item_code, 
							pr_item.description,
							pr_item.qty, 
							pr_item.base_rate, 
							pr_item.base_amount, 
							pr_item.name,
							pr_item.warehouse,
							pr_item.project,
							pr_item.cost_center, 
							pr_item.is_fixed_asset,
							pr_item.parent,
							pr_item.parenttype

						from 
							`tab{doctype} Item` pr_item 
						where 
							parent = %s
							and exists(
										select name 
										from tabItem
										where 
											name = pr_item.item_code 
											and (is_stock_item = 1 or is_fixed_asset=1)
									)
					""".format(
						doctype=pr.receipt_document_type
					),
					pr.receipt_document,
					as_dict=True,
				)

				for d in pr_items:
					if not d.warehouse:
						d.warehouse = frappe.get_value(d.parenttype, d.parent, "set_warehouse")
						
					if not d.project:
						d.project = frappe.get_value(d.parenttype, d.parent, "project")

					item = self.append("items")
					item.item_code = d.item_code
					item.description = d.description
					item.qty = d.qty
					item.rate = d.base_rate
					item.cost_center = d.cost_center or erpnext.get_default_cost_center(self.company)
					item.amount = d.base_amount
					item.receipt_document_type = pr.receipt_document_type
					item.receipt_document = pr.receipt_document
					item.purchase_receipt_item = d.name
					item.is_fixed_asset = d.is_fixed_asset
					# add
					item.warehouse = d.warehouse
					item.project = d.project


	