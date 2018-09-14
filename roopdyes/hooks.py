# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "roopdyes"
app_title = "RoopDyes"
app_publisher = "FinByz Tech Pvt Ltd"
app_description = "Roopdyes App"
app_icon = "fa fa-flask"
app_color = "#FF888B"
app_email = "info@finbyz.com"
app_license = "GPL 3.0"

# Includes in <head>
# ------------------

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

override_whitelisted_methods = {
	"erpnext.manufacturing.doctype.bom_update_tool.bom_update_tool.enqueue_update_cost": "roopdyes.api.enqueue_update_cost"
}


doc_events = {
	"Stock Entry": {
		"before_submit": "roopdyes.api.override_po_functions",
		"on_submit": "roopdyes.api.se_on_submit"
	},
	"BOM": {
		"before_save": "roopdyes.api.bom_before_save",
	},
}

scheduler_events = {
	"daily":[
		"roopdyes.api.upadte_item_price_daily"
	]
}