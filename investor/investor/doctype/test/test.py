# Copyright (c) 2025, alaalsalam and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class test(Document):
	@frappe.whitelist()
	def save_logs(logs):
		logs = frappe.parse_json(logs)
		for log in logs:
			# إنشاء سجل جديد في DocType "Log Entry"
			doc = frappe.get_doc({
				"doctype": "Log Entry",
				"log_type": log.get("log_type"),
				"time": log.get("time"),
			})
			doc.insert()
		return {"message": "Logs saved successfully!"}


#  # في دالة الـ validate الخاصة بالـ Doctype 'test'
# 	def validate(self):
# 		frappe.msgprint("hi")
# 		for row in self.test:
# 			# الحصول على قيمة dividend من السجل الفرعي
# 			dividend = row.dividend
			
# 			# حساب قيمة profit_amount بناءً على النسبة
# 			if dividend:
# 				row.profit_amount = 30 * (dividend / 100)
			
# 			# طباعة رسالة للتأكد من الحساب
# 			print(f"Dividend: {dividend}%")
# 			print(f"Calculated Profit Amount: {row.profit_amount}")

