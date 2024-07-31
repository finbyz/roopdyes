# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "roopdyes"
app_title = "RoopDyes"
app_publisher = "FinByz Tech Pvt Ltd"
app_description = "Roopdyes App"
app_icon = "finbyz finbyz-chemical"
app_color = "#FF888B"
app_email = "info@finbyz.com"
app_license = "GPL 3.0"

# Includes in <head>
# ------------------


app_include_js = [
	# "assets/js/summernote.min.js",
	# "assets/js/comment_desk.min.js",
	# "assets/js/editor.min.js",
	# "assets/js/timeline.min.js"
]

app_include_css = [
	# "assets/css/summernote.min.css"
]

# include js, css files in header of desk.html
# app_include_css = "/assets/roopdyes/css/roopdyes.css"
# app_include_js = "/assets/roopdyes/js/roopdyes.js"

# include js, css files in header of web template
# web_include_css = "/assets/roopdyes/css/roopdyes.css"
# web_include_js = "/assets/roopdyes/js/roopdyes.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "roopdyes.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "roopdyes.install.before_install"
# after_install = "roopdyes.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "roopdyes.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"roopdyes.tasks.all"
# 	],
# 	"daily": [
# 		"roopdyes.tasks.daily"
# 	],
# 	"hourly": [
# 		"roopdyes.tasks.hourly"
# 	],
# 	"weekly": [
# 		"roopdyes.tasks.weekly"
# 	]
# 	"monthly": [
# 		"roopdyes.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "roopdyes.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "roopdyes.event.get_events"
# }
# fixtures = ["Custom Field"]

override_whitelisted_methods = {
	# "erpnext.manufacturing.doctype.bom_update_tool.bom_update_tool.enqueue_update_cost": "roopdyes.api.enqueue_update_cost"
}


doc_events = {
	# "Stock Entry": {
	# 	"validate": "roopdyes.batch_valuation.stock_entry_validate",
	# 	"before_submit": "roopdyes.api.override_po_functions",
	# 	"on_submit": [
	# 		"roopdyes.api.se_on_submit",
	# 		"roopdyes.batch_valuation.stock_entry_on_submit",
	# 	],
	# 	"before_cancel": [
	# 		"roopdyes.api.override_po_functions",
	# 		"roopdyes.api.stock_entry_before_cancel",
	# 	],
	# 	"on_cancel":[
	# 		"roopdyes.batch_valuation.stock_entry_on_cancel",
	# 		"roopdyes.api.stock_entry_on_cancel"
	# 	]
	# },
	# "BOM": {
	# 	"before_save": "roopdyes.api.bom_before_save",
	# 	"on_update_after_submit": "roopdyes.api.bom_on_update"
	# },
	# "Sales Invoice": {
	# 	"on_submit": "roopdyes.api.si_on_submit",
	# 	"on_cancel": "roopdyes.api.si_on_cancel"
	# },
	# "Batch": {
	# 	'before_naming': "roopdyes.batch_valuation.override_batch_autoname",
	# },
	# "Purchase Receipt": {
	# 	"validate": "roopdyes.batch_valuation.pr_validate",
	# 	"on_cancel": "roopdyes.batch_valuation.pr_on_cancel",
	# },
	# "Purchase Invoice": {
	# 	"validate": "roopdyes.batch_valuation.pi_validate",
	# 	"on_submit": "roopdyes.api.pi_on_submit",
	# 	"on_cancel": ["roopdyes.batch_valuation.pi_on_cancel","roopdyes.api.pi_on_cancel"],
	# },
	# "Landed Cost Voucher": {
	# 	"validate": "roopdyes.batch_valuation.lcv_validate",
	# 	"on_submit": "roopdyes.batch_valuation.lcv_on_submit",
	# 	"on_cancel": [
	# 		"roopdyes.batch_valuation.lcv_on_cancel",
	# 	],
	# },
	# "Stock Ledger Entry": {
	# 	"before_submit": "roopdyes.api.sl_before_submit"
	# },
	# ("Sales Invoice", "Purchase Invoice", "Payment Request", "Payment Entry", "Journal Entry", "Material Request", "Purchase Order", "Work Order", "Production Plan", "Stock Entry", "Quotation", "Sales Order", "Delivery Note", "Purchase Receipt", "Packing Slip"): {
	# 	"before_naming": "roopdyes.api.docs_before_naming",
	# }
}

scheduler_events = {
	# "daily":[
	# 	"roopdyes.api.upadte_item_price_daily"
	# ]
}

doctype_js = {
	# "Stock Entry": "public/js/doctype_js/stock_entry.js",
}

# Chemical Overrides

# from roopdyes.batch_valuation_overrides import get_supplied_items_cost,set_incoming_rate_buying,set_incoming_rate_selling,get_rate_for_return,get_incoming_rate,process_sle,get_args_for_incoming_rate

# Buying controllers
# from erpnext.controllers.buying_controller import BuyingController
# BuyingController.get_supplied_items_cost = get_supplied_items_cost
# BuyingController.set_incoming_rate = set_incoming_rate_buying

# # Selling controllers
# from erpnext.controllers.selling_controller import SellingController
# SellingController.set_incoming_rate = set_incoming_rate_selling

# # sales and purchase return
# from erpnext.controllers import sales_and_purchase_return
# sales_and_purchase_return.get_rate_for_return =  get_rate_for_return

# utils

# from erpnext.stock import utils
# utils.get_incoming_rate =  get_incoming_rate

# import erpnext
# erpnext.stock.utils.get_incoming_rate = get_incoming_rate

# # stock_ledger
# from erpnext.stock.stock_ledger import update_entries_after
# update_entries_after.process_sle =  process_sle

# # stock entry
# from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
# StockEntry.get_args_for_incoming_rate = get_args_for_incoming_rate


# from erpnext.controllers.stock_controller import StockController
# from roopdyes.api import delete_auto_created_batches
# StockController.delete_auto_created_batches = delete_auto_created_batches
