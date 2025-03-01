

from erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher import LandedCostVoucher

import frappe
import erpnext
import re
from frappe.model.document import Document
from frappe.query_builder.custom import ConstantColumn

from frappe import _
from erpnext.controllers.accounts_controller import AccountsController
from frappe.utils import getdate, nowdate
from frappe.utils import money_in_words
from erpnext.accounts.doctype.payment_request.payment_request import \
    make_payment_request
from frappe.utils.csvutils import getlink
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.accounts.general_ledger import make_reverse_gl_entries

from frappe.utils import (
	flt,
 )
from erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher import LandedCostVoucher

class LandedCostVoucherCustom(AccountsController,LandedCostVoucher):
	def validate(self):
		pass
	def on_submit(self):
		if self.custom_supplier_or_expense=="Account":
			self.make_gl_entries()

	def make_gl_entries(self, cancel=False, from_repost=False): 
		
		gl_entries = self.get_gl_entries() 

		if gl_entries: 
			make_gl_entries( 
				gl_entries, 
				cancel=cancel, 
				update_outstanding="No", 
				merge_entries=False, 
				from_repost=from_repost 
			) 

	def get_gl_entries(self): 
		gl_entries = [] 
		self.record_initial_entry(gl_entries) 
		
		return gl_entries 

	def record_initial_entry(self, gl_entries):  
		if self.custom_supplier_or_expense=="Account":	
			for tax_row in self.taxes:
				if tax_row.amount > 0:
					gl_entries.append(
						self.get_gl_dict({
							"account": tax_row.expense_account or self.expense_account,
							"debit": tax_row.amount,
							"credit": 0,
							"posting_date": frappe.utils.today(),
							"against": tax_row.custom_account or self.custom_account,
							"company": self.company,
							"remarks": "No Remarks"
						})
					)

					gl_entries.append(
						self.get_gl_dict({
							"account": tax_row.custom_account or self.custom_account,
							"credit": tax_row.amount,
							"debit": 0,
							"posting_date": frappe.utils.today(),
							"against": tax_row.expense_account or self.expense_account,
							"company": self.company,
							"remarks": "No Remarks"
						})
		
					)
	@staticmethod
	def get_pr_items(purchase_receipt):
		item = frappe.qb.DocType("Item")
		pr_item = frappe.qb.DocType(purchase_receipt.receipt_document_type + " Item")
		return (
			frappe.qb.from_(pr_item)
			.inner_join(item)
			.on(item.name == pr_item.item_code)
			.select(
				pr_item.item_code,
				pr_item.description,
				pr_item.qty,
				pr_item.base_rate,
				pr_item.base_amount,
				pr_item.name,
				pr_item.cost_center,
				pr_item.is_fixed_asset,
				pr_item.project,
				ConstantColumn(purchase_receipt.receipt_document_type).as_("receipt_document_type"),
				ConstantColumn(purchase_receipt.receipt_document).as_("receipt_document"),
			)
			.where(
				(pr_item.parent == purchase_receipt.receipt_document)
				& ((item.is_stock_item == 1) | (item.is_fixed_asset == 1))
			)
			.run(as_dict=True)
		)

	@frappe.whitelist()
	def get_items_from_purchase_receipts(self):
		self.set("items", [])
		for pr in self.get("purchase_receipts"):
			if pr.receipt_document_type and pr.receipt_document:
				pr_items = self.get_pr_items(pr)

				for d in pr_items:
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
					item.custom_project = d.project if hasattr(d, "project") else None

				

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


	