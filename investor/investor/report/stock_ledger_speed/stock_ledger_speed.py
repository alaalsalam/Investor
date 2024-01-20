# Copyright (c) 2023, alaalsalam and contributors
# For license information, please see license.txt

# import frappe


from tokenize import String
import frappe
from frappe import _
from frappe.utils import cint, flt

from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.stock.utils import (
	is_reposting_item_valuation_in_progress,
	update_included_uom_in_report,
)


def execute(filters=None):
	is_reposting_item_valuation_in_progress()
	include_uom = filters.get("include_uom")
	columns = get_columns()
	items = get_items(filters)
	sl_entries = get_stock_ledger_entries(filters, items)
	item_details = get_item_details(items, sl_entries, include_uom)
	opening_row = get_opening_balance(filters, columns, sl_entries)
	precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))

	data = []
	conversion_factors = []
	if opening_row:
		data.append(opening_row)
		conversion_factors.append(0)

	actual_qty = stock_value = 0

	available_serial_nos = {}
	for sle in sl_entries:
		item_detail = item_details[sle.item_code]

		sle.update(item_detail)

		if filters.get("batch_no"):
			actual_qty += flt(sle.actual_qty, precision)
			stock_value += sle.stock_value_difference

			if sle.voucher_type == "Stock Reconciliation" and not sle.actual_qty:
				actual_qty = sle.qty_after_transaction
				stock_value = sle.stock_value

			sle.update({"qty_after_transaction": actual_qty, "stock_value": stock_value})

		sle.update({
			"in_qty": max(sle.actual_qty, 0),
			"out_qty": min(sle.actual_qty, 0),
			"t_warehouse": sle.warehouse if max(sle.actual_qty, 0) > 0 else "",
			"s_warehouse": sle.warehouse if min(sle.actual_qty, 0) < 0 else ""
			})

		if sle.serial_no:
			update_available_serial_nos(available_serial_nos, sle)

		data.append(sle)

		if include_uom:
			conversion_factors.append(item_detail.conversion_factor)

	update_included_uom_in_report(columns, data, include_uom, conversion_factors)
	
	if filters.get("type")=="Material Transfer":
		data2 = []
		for d2 in data:
			for d1 in data:
				if d1.item==d2.item and d1.voucher_no == d2.voucher_no and d1.actual_qty != d2.actual_qty and d1.in_qty == -(d2.out_qty) and d1.warehouse != d2.warehouse:					
					d1.update({ 
						"in_qty": d1.in_qty if d1.in_qty else d2.in_qty,
						"out_qty": d1.out_qty if d1.out_qty else d2.out_qty,
						"t_warehouse": d1.t_warehouse if d1.t_warehouse else d2.t_warehouse,
						"s_warehouse": d1.s_warehouse if d1.s_warehouse else d2.s_warehouse,
						})
					data2.append(d1)
					data.remove(d1)
					data.remove(d2)				
					# break
		data = data2
		columns[8]['label'] = "Qut" 
		columns = [i for i in columns if not (i['fieldname'] == "out_qty")]
	if filters.get("type")=="Material Receipt":
		columns = [i for i in columns if not (i['fieldname'] == "out_qty")]
		columns = [i for i in columns if not (i['fieldname'] == "s_warehouse")]

	if filters.get("type")=="Material Issue":
		columns = [i for i in columns if not (i['fieldname'] == "in_qty")]
		columns = [i for i in columns if not (i['fieldname'] == "t_warehouse")]
					

		
	# return col, data
	return columns, data


def update_available_serial_nos(available_serial_nos, sle):
	serial_nos = get_serial_nos(sle.serial_no)
	key = (sle.item_code, sle.warehouse)
	if key not in available_serial_nos:
		available_serial_nos.setdefault(key, [])

	existing_serial_no = available_serial_nos[key]
	for sn in serial_nos:
		if sle.actual_qty > 0:
			if sn in existing_serial_no:
				existing_serial_no.remove(sn)
			else:
				existing_serial_no.append(sn)
		else:
			if sn in existing_serial_no:
				existing_serial_no.remove(sn)
			else:
				existing_serial_no.append(sn)

	sle.balance_serial_no = "\n".join(existing_serial_no)


def get_columns():
	columns = [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Datetime", "width": 120},
		{
			"label": _("Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 100,
		},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 100},
		{
			"label": _("UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 60,
		},
		{
			"label": _("Type"),
			"fieldname": "type",
			"fieldtype": "Text",
			"width": 120,
			"convertible": "qty",
		},
		{
			"label": _("Source Warehouse"),
			"fieldname": "s_warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 150,
		},
		{
			"label": _("Out Qty"),
			"fieldname": "out_qty",
			"fieldtype": "Float",
			"width": 70,
			"convertible": "qty",
		},
		{
			"label": _("Target Warehouse"),
			"fieldname": "t_warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 150,
		},
		{
			"label": _("In Qty"),
			"fieldname": "in_qty",
			"fieldtype": "Float",
			"width": 70,
			"convertible": "qty",
		},	
		{
			"label": _("Voucher #"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 150,
		},
	
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 100,
		},
		{
			"label": _("Brand"),
			"fieldname": "brand",
			"fieldtype": "Link",
			"options": "Brand",
			"width": 100,
		},
		{"label": _("Description"), "fieldname": "description", "width": 200},
		{
			"label": _("Incoming Rate"),
			"fieldname": "incoming_rate",
			"fieldtype": "Currency",
			"width": 110,
			"options": "Company:company:default_currency",
			"convertible": "rate",
		},
		{
			"label": _("Valuation Rate"),
			"fieldname": "valuation_rate",
			"fieldtype": "Currency",
			"width": 110,
			"options": "Company:company:default_currency",
			"convertible": "rate",
		},
		{
			"label": _("Balance Value"),
			"fieldname": "stock_value",
			"fieldtype": "Currency",
			"width": 110,
			"options": "Company:company:default_currency",
		},
		{
			"label": _("Value Change"),
			"fieldname": "stock_value_difference",
			"fieldtype": "Currency",
			"width": 110,
			"options": "Company:company:default_currency",
		},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 110},
		{
			"label": _("Voucher #"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 100,
		},
		{
			"label": _("Batch"),
			"fieldname": "batch_no",
			"fieldtype": "Link",
			"options": "Batch",
			"width": 100,
		},
		{
			"label": _("Serial No"),
			"fieldname": "serial_no",
			"fieldtype": "Link",
			"options": "Serial No",
			"width": 100,
		},
		{"label": _("Balance Serial No"), "fieldname": "balance_serial_no", "width": 100},
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 100,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 110,
		},
	]

	return columns


def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ""
	if items:
		item_conditions_sql = "and sle.item_code in ({})".format(
			", ".join(frappe.db.escape(i) for i in items)
		)

	sl_entries = frappe.db.sql(
		"""
		SELECT
			concat_ws(" ", sle.posting_date, sle.posting_time) AS date,
			sle.item_code,
			sle.warehouse,
			sle.actual_qty,
			sle.qty_after_transaction,
			sle.incoming_rate,
			sle.valuation_rate,
			sle.stock_value,
			sle.voucher_type,
			sle.voucher_no,
			sle.batch_no,
			sle.serial_no,
			sle.company,
			sle.project,
			sle.stock_value_difference,
			se.stock_entry_type type
		FROM
			`tabStock Ledger Entry` sle
				join `tabStock Entry` se
               		on se.name = sle.voucher_no
		WHERE
			sle.company = %(company)s
				AND sle.is_cancelled = 0 AND sle.posting_date BETWEEN %(from_date)s AND %(to_date)s
				{sle_conditions}
				{item_conditions_sql}
		ORDER BY
			sle.posting_date asc, sle.posting_time asc, sle.creation asc
		""".format(
			sle_conditions=get_sle_conditions(filters), item_conditions_sql=item_conditions_sql
		),
		filters,
		as_dict=1,
	)

	return sl_entries


def get_items(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")
	else:
		if filters.get("brand"):
			conditions.append("item.brand=%(brand)s")
		if filters.get("item_group"):
			conditions.append(get_item_group_condition(filters.get("item_group")))

	items = []
	if conditions:
		items = frappe.db.sql_list(
			"""select name from `tabItem` item where {}""".format(" and ".join(conditions)), filters
		)
	return items


def get_item_details(items, sl_entries, include_uom):
	item_details = {}
	if not items:
		items = list(set(d.item_code for d in sl_entries))

	if not items:
		return item_details

	cf_field = cf_join = ""
	if include_uom:
		cf_field = ", ucd.conversion_factor"
		cf_join = (
			"left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom=%s"
			% frappe.db.escape(include_uom)
		)

	res = frappe.db.sql(
		"""
		select
			item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom {cf_field}
		from
			`tabItem` item
			{cf_join}
		where
			item.name in ({item_codes})
	""".format(
			cf_field=cf_field, cf_join=cf_join, item_codes=",".join(["%s"] * len(items))
		),
		items,
		as_dict=1,
	)

	for item in res:
		item_details.setdefault(item.name, item)

	return item_details


def get_sle_conditions(filters):
	conditions = []
	if filters.get("warehouse"):
		if filters.get("type")=="Material Transfer":
			warehouse_condition = get_warehouse_condition_transfar(filters.get("warehouse"))
		else:
			warehouse_condition = get_warehouse_condition(filters.get("warehouse"))
			
		
		if warehouse_condition:
			conditions.append(warehouse_condition)

	if filters.get("voucher_no"):
		conditions.append("voucher_no=%(voucher_no)s")
	if filters.get("batch_no"):
		conditions.append("batch_no=%(batch_no)s")
	if filters.get("project"):
		conditions.append("project=%(project)s")
	# if filters.get("item group"):
	# 	conditions.append("item_group=%(item_group)s")
	# if filters.get("brand"):
	# 	conditions.append("brand=%(brand)s")
	if filters.get("type"):
		conditions.append("se.stock_entry_type=%(type)s")

	return "and {}".format(" and ".join(conditions)) if conditions else ""


def get_opening_balance(filters, columns, sl_entries):
	if not (filters.item_code and filters.warehouse and filters.from_date):
		return

	from erpnext.stock.stock_ledger import get_previous_sle

	last_entry = get_previous_sle(
		{
			"item_code": filters.item_code,
			"warehouse_condition": get_warehouse_condition(filters.warehouse),
			"posting_date": filters.from_date,
			"posting_time": "00:00:00",
		}
	)

	# check if any SLEs are actually Opening Stock Reconciliation
	for sle in sl_entries:
		if (
			sle.get("voucher_type") == "Stock Reconciliation"
			and sle.get("date").split()[0] == filters.from_date
			and frappe.db.get_value("Stock Reconciliation", sle.voucher_no, "purpose") == "Opening Stock"
		):
			last_entry = sle
			sl_entries.remove(sle)

	row = {
		"item_code": _("'Opening'"),
		"qty_after_transaction": last_entry.get("qty_after_transaction", 0),
		"valuation_rate": last_entry.get("valuation_rate", 0),
		"stock_value": last_entry.get("stock_value", 0),
	}

	return row


def get_warehouse_condition(warehouse):
	warehouse_details = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"], as_dict=1)
	if warehouse_details:
		return (
			" exists (select name from `tabWarehouse` wh \
			where wh.lft >= %s and wh.rgt <= %s and warehouse = wh.name)"
			% (warehouse_details.lft, warehouse_details.rgt)
		)

	return ""

def get_warehouse_condition_transfar(warehouse):
	warehouse_details = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"], as_dict=1)
	if warehouse_details:
		return (
			" exists (select name from `tabWarehouse` wh \
			where wh.lft >= %s or wh.rgt <= %s and warehouse = wh.name)"
			% (warehouse_details.lft, warehouse_details.rgt)
		)

	return ""


def get_item_group_condition(item_group):
	item_group_details = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=1)
	if item_group_details:
		return (
			"item.item_group in (select ig.name from `tabItem Group` ig \
			where ig.lft >= %s and ig.rgt <= %s and item.item_group = ig.name)"
			% (item_group_details.lft, item_group_details.rgt)
		)

	return ""
