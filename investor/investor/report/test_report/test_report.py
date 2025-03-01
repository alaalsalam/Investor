# Copyright (c) 2025, alaalsalam and contributors
# For license information, please see license.txt

# import frappe


import frappe

def execute(filters=None):
    columns, data = [], []
    
    # حدد الأعمدة بناءً على القيم الفريدة للحقل cost_type
    cost_types = frappe.db.sql_list("""
        SELECT DISTINCT cost_type 
        FROM `tabCost Table`
    """)

    # إعداد الأعمدة
    columns = [{"label": cost_type, "fieldname": cost_type.lower().replace(" ", "_"), "fieldtype": "Currency"} 
                for cost_type in cost_types]

    # جلب بيانات التكاليف من الجدول
    parent_records = frappe.get_all("test", fields=["name"])
    
    for record in parent_records:
        row_data = {cost_type.lower().replace(" ", "_"): 0 for cost_type in cost_types}
        
        # جلب القيم لكل سجل Parent
        child_records = frappe.get_all("Cost Table", filters={"parent": record.name}, fields=["cost_type", "amount"])
        
        for child in child_records:
            key = child.cost_type.lower().replace(" ", "_")
            if key in row_data:
                row_data[key] = child.amount

        # إضافة الصف إلى البيانات
        data.append(row_data)

    return columns, data
