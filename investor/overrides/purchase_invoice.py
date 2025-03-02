from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
import frappe

class CustomPurchaseInvoice(PurchaseInvoice):
    def update_project(self):
        projects = frappe._dict()
        for d in self.items:
            if d.project:
                if self.docstatus == 1:
                    projects[d.project] = projects.get(d.project, 0) + d.base_net_amount
                elif self.docstatus == 2:
                    projects[d.project] = projects.get(d.project, 0) - d.base_net_amount

        pj = frappe.qb.DocType("Project")
        for proj, value in projects.items():
            res = frappe.qb.from_(pj).select(pj.total_purchase_cost).where(pj.name == proj).for_update().run()
            current_purchase_cost = res and res[0][0] or 0

            project_doc = frappe.get_doc("Project", proj)
            project_doc.total_purchase_cost = current_purchase_cost + value
            project_doc.custom_project_cost = current_purchase_cost + value

            project_doc.calculate_gross_margin()
            project_doc.db_update()
