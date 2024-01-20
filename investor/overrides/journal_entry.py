from erpnext.accounts.doctype.journal_entry.journal_entry import JournalEntry

from frappe.utils import cint, cstr, flt, fmt_money, formatdate, get_link_to_form, nowdate

class JournalEntryCustom(JournalEntry):
	  
	def build_gl_map(self):
		gl_map = []
		for d in self.get("accounts"):
			if d.debit or d.credit or (self.voucher_type == "Exchange Gain Or Loss"):
				# r = [d.user_remark, self.remark]
				# r = [x for x in r if x]
				remarks = d.user_remark
				posting_date = d.custom_posting_date
    
				gl_map.append(
					self.get_gl_dict(
						{
							"account": d.account,
							"party_type": d.party_type,
							"due_date": self.due_date,
							"party": d.party,
							"against": d.against_account,
							"debit": flt(d.debit, d.precision("debit")),
							"credit": flt(d.credit, d.precision("credit")),
							"account_currency": d.account_currency,
							"debit_in_account_currency": flt(
								d.debit_in_account_currency, d.precision("debit_in_account_currency")
							),
							"credit_in_account_currency": flt(
								d.credit_in_account_currency, d.precision("credit_in_account_currency")
							),
							"against_voucher_type": d.reference_type,
							"against_voucher": d.reference_name,
							"remarks": remarks,
							"voucher_detail_no": d.reference_detail_no,
							"cost_center": d.cost_center,
							"project": d.project,
							"finance_book": self.finance_book,
							"posting_date": posting_date,
						},
						item=d,
					)
				)
		return gl_map


def set_post_data(doc, method):
    for d in doc.get("accounts"):
        if not d.custom_posting_date:
            d.custom_posting_date = doc.posting_date