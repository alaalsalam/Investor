# # Copyright (c) 2023, alaalsalam and contributors
# # For license information, please see license.txt


import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Name"), "fieldname": "name", "fieldtype": "Link", "options": "Landed Cost Voucher", "width": 160},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Data", "width": 120},
        {"label": _("Docstatus"), "fieldname": "docstatus", "fieldtype": "Data", "width": 100},
        {"label": _("Applicable Charges"), "fieldname": "applicable_charges", "fieldtype": "Float", "width": 140},
    ]

    custom_item_codes = frappe.db.sql_list("""
        SELECT DISTINCT custom_item_code
        FROM `tabLanded Cost Taxes and Charges`
        WHERE custom_item_code IS NOT NULL
    """)

    for custom_item_code in custom_item_codes:
        columns.append({
            "label": custom_item_code,
            "fieldname": custom_item_code.lower().replace(" ", "_"),
            "fieldtype": "HTML",  
            "width": 140
        })

    conditions = []
    if filters.get("item_code"):
        conditions.append(f"lci.item_code = '{filters['item_code']}'")
    if filters.get("from_date"):
        conditions.append(f"lcv.posting_date >= '{filters['from_date']}'")
    if filters.get("to_date"):
        conditions.append(f"lcv.posting_date <= '{filters['to_date']}'")
        

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    raw_data = frappe.db.sql(f"""
        SELECT
            lcv.name, lci.item_code, lcv.docstatus, lctc.custom_item_code, 
            lctc.amount, lctc.description, lcv.posting_date,
            CASE
                WHEN '{filters.get("distribute_charges_based_on", "qty")}' = 'qty' THEN
                    lctc.amount * lci.qty / (SELECT SUM(qty) FROM `tabLanded Cost Item` WHERE parent = lcv.name)
                WHEN '{filters.get("distribute_charges_based_on", "amount")}' = 'amount' THEN
                    lctc.amount * lci.amount / (SELECT SUM(amount) FROM `tabLanded Cost Item` WHERE parent = lcv.name)
                ELSE 0
            END AS applicable_charges
        FROM
            `tabLanded Cost Voucher` lcv
        LEFT JOIN
            `tabLanded Cost Taxes and Charges` lctc ON lcv.name = lctc.parent
        LEFT JOIN
            `tabLanded Cost Item` lci ON lcv.name = lci.parent
        {where_clause}  
        ORDER BY lci.item_code, lcv.name
    """, as_dict=True)

    group_by_item = filters.get("group_by_item_code", 0)
    show_description = filters.get("show_description", 0)

    grouped_data = {}

    for row in raw_data:
        key = row.item_code if group_by_item else (row.name, row.item_code)

        if key not in grouped_data:
            grouped_data[key] = {
                "name": row.name if not group_by_item else _("Multiple"),
                "item_code": row.item_code,
                "docstatus": row.docstatus if not group_by_item else "-",
                "applicable_charges": 0,
                "posting_date": row.posting_date,
            }

        grouped_data[key]["applicable_charges"] += row.applicable_charges or 0

        if row.custom_item_code:
            fieldname = row.custom_item_code.lower().replace(" ", "_")

            if fieldname not in grouped_data[key]:
                grouped_data[key][fieldname] = 0 

            if not show_description or group_by_item:
                grouped_data[key][fieldname] += row.applicable_charges or 0  
            else:
                existing_value = grouped_data[key][fieldname]
                
                if isinstance(existing_value, (int, float)):
                    existing_value = f"{existing_value:.2f}" if existing_value != 0 else ""

                new_value = f"{row.applicable_charges:.2f}" if row.applicable_charges else "0.00"
                description_text = f"<br><span style='color:gray; font-size:10px;'>{row.description}</span>" if row.description else ""

                if existing_value:
                    grouped_data[key][fieldname] = f"{existing_value} + {new_value}{description_text}"
                else:
                    grouped_data[key][fieldname] = f"{new_value}{description_text}"

    report_data = list(grouped_data.values())

    return columns, report_data
#