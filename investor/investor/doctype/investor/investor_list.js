frappe.listview_settings['Investor'] = {
	add_fields: ["investor_name", "investor_group", "image", "on_hold"],
	get_indicator: function(doc) {
		if(cint(doc.on_hold)) {
			return [__("On Hold"), "red"];
		}
	}
};
