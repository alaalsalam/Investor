
__version__ = '0.0.1'
import frappe
import erpnext.accounts.general_ledger as general_ledger_module
from frappe.utils import getdate, formatdate 
from frappe import _
from erpnext.accounts.doctype.accounting_dimension_filter.accounting_dimension_filter import (
	get_dimension_filter_map,
)
from erpnext.accounts.general_ledger import (
    validate_cwip_accounts,
    process_debit_credit_difference,
    
    check_freezing_date,
    validate_allowed_dimensions,
    make_entry,
)
import erpnext.accounts.general_ledger as general_ledger_module

def custom_save_entries(gl_map, adv_adj, update_outstanding, from_repost=False):
   
    if not from_repost:
        validate_cwip_accounts(gl_map)

    process_debit_credit_difference(gl_map)

    dimension_filter_map = get_dimension_filter_map()
    if gl_map:
        check_freezing_date(gl_map[0]["posting_date"], adv_adj)
        is_opening = any(d.get("is_opening") == "Yes" for d in gl_map)
        project = gl_map[0].get("project")
        if gl_map[0]["voucher_type"] != "Period Closing Voucher":
            custom_validate_against_pcv(is_opening, gl_map[0]["posting_date"], gl_map[0]["company"], project)

    for entry in gl_map:
        validate_allowed_dimensions(entry, dimension_filter_map)
        make_entry(entry, adv_adj, update_outstanding, from_repost)

general_ledger_module.save_entries = custom_save_entries



def custom_validate_against_pcv(is_opening, posting_date, company, project):
    if is_opening and frappe.db.exists("Period Closing Voucher", {"docstatus": 1, "company": company}):
        frappe.throw(
            _("Opening Entry can not be created after Period Closing Voucher is created."),
            title=_("Invalid Opening Entry"),
        )

    if project:
        project_status = frappe.db.get_value("Project", project, "status")
        if project_status == "Completed":
            frappe.throw(
                _("You cannot create new invoices for the project '{0}' as it is marked as Completed.").format(project),
                title=_("Project Closed"),
            )

    else:
        last_closing_voucher = frappe.db.get_value(
            "Period Closing Voucher",
            {"docstatus": 1, "company": company},
            ["max(period_end_date)", "custom_project"],
            as_dict=True,
        )

        if last_closing_voucher:
            last_pcv_date = last_closing_voucher.get("max(period_end_date)")
            custom_project_in_closure = last_closing_voucher.get("custom_project")

            if custom_project_in_closure:
                frappe.msgprint(
                    _("The latest closure is specific to the project '{0}', so it does not affect this entry.").format(custom_project_in_closure),
                    title=_("Project-Specific Closure"),
                )
            elif last_pcv_date and getdate(posting_date) <= getdate(last_pcv_date):
                message = _("Books have been closed till the period ending on {0}").format(formatdate(last_pcv_date))
                message += "</br >"
                message += _("You cannot create/amend any accounting entries till this date.")
                frappe.throw(message, title=_("Period Closed"))


# general_ledger_module.validate_against_pcv = custom_validate_against_pcv

# # def save_entries(gl_map, adv_adj, update_outstanding, from_repost=False):
# #     if not from_repost:
# #         validate_cwip_accounts(gl_map)

# #     process_debit_credit_difference(gl_map)

# #     dimension_filter_map = get_dimension_filter_map()
# #     if gl_map:
# #         check_freezing_date(gl_map[0]["posting_date"], adv_adj)
# #         is_opening = any(d.get("is_opening") == "Yes" for d in gl_map)
        
# #         project = gl_map[0].get("project")  # تأكد من أن project موجودة في الإدخالات
        
# #         # تمرير المشروع عند استدعاء validate_against_pcv
# #         if gl_map[0]["voucher_type"] != "Period Closing Voucher":
# #             validate_against_pcv(is_opening, gl_map[0]["posting_date"], gl_map[0]["company"], project)

# #     for entry in gl_map:
# #         validate_allowed_dimensions(entry, dimension_filter_map)
# #         make_entry(entry, adv_adj, update_outstanding, from_repost)
