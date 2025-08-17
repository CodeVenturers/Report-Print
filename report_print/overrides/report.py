# Copyright (c) 2024, Code Venturers and contributors
# For license information, please see license.txt


import frappe
import os
from frappe.desk.query_report import get_report_doc
from frappe.modules import get_module_path, scrub
from frappe.model.utils import render_include
from frappe.utils import get_html_format



@frappe.whitelist()
def get_script(report_name):
	report = get_report_doc(report_name)
	module = report.module or frappe.db.get_value("DocType", report.ref_doctype, "module")

	is_custom_module = frappe.get_cached_value("Module Def", module, "custom")

	# custom modules are virtual modules those exists in DB but not in disk.
	module_path = "" if is_custom_module else get_module_path(module)
	report_folder = module_path and os.path.join(module_path, "report", scrub(report.name))

	report_override_js = frappe.get_hooks("report_override_js", {})
	if report_override_js.get(report_name):
		script_path = os.path.join(frappe.get_app_path("test"), report_override_js.get(report_name)[0])
	else:
		script_path = report_folder and os.path.join(report_folder, scrub(report.name) + ".js")

	script = None
	if os.path.exists(script_path):
		with open(script_path) as f:
			script = f.read()
			script += f"\n\n//# sourceURL={scrub(report.name)}.js"

	if report_print := frappe.db.get_value(
		"Report Print Format", {"default": 1, "report": report.name, "disabled": 0}, "html"
	):
		html_format = report_print
	else:
		print_path = report_folder and os.path.join(
			report_folder, scrub(report.name) + ".html"
		)
		html_format = get_html_format(print_path)

	if not script and report.javascript:
		script = report.javascript
		script += f"\n\n//# sourceURL={scrub(report.name)}__custom"

	if not script:
		script = "frappe.query_reports['%s']={}" % report_name

	return {
		"script": render_include(script),
		"html_format": html_format,
		"execution_time": 0,
		"filters": report.filters,
		"custom_report_name": report.name if report.get("is_custom_report") else None,
	}
