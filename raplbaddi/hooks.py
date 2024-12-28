from . import __version__ as app_version

app_name = "raplbaddi"
app_title = "Raplbaddi"
app_publisher = "Nishant Bhickta"
app_description = "Custom app for Real Appliances Private Limited Baddi"
app_email = "nishantbhickta@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/raplbaddi/css/raplbaddi.css"
# app_include_js = "/assets/raplbaddi/js/raplbaddi.js"

# include js, css files in header of web template
# web_include_css = "/assets/raplbaddi/css/raplbaddi.css"
# web_include_js = "/assets/raplbaddi/js/raplbaddi.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "raplbaddi/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Purchase Order": "public/js/purchase_order.js",
    "Purchase Receipt": "public/js/purchase_receipt.js",
    "Sales Order": "public/js/sales_order.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "raplbaddi.utils.jinja_methods",
# 	"filters": "raplbaddi.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "raplbaddi.install.before_install"
# after_install = "raplbaddi.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "raplbaddi.uninstall.before_uninstall"
# after_uninstall = "raplbaddi.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "raplbaddi.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes


override_doctype_class = {
	"Purchase Receipt": "raplbaddi.overrides.purchase_receipt.PurchaseReceipt",
	# "Purchase Order": "raplbaddi.overrides.purchase_order.PurchaseOrder",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "User Permission": {
        "validate": [
            "raplbaddi.overrides.user_permissions.validate",
        ],
        "on_trash": [
            "raplbaddi.overrides.user_permissions.validate",
        ],
    },
    "Delivery Note": {
        "before_insert": [
            "raplbaddi.overrides.delivery_note.before_insert",
        ],
        "validate": [
            "raplbaddi.overrides.delivery_note.validate",
        ],
        "on_submit": [
            "raplbaddi.overrides.delivery_note.on_submit",
        ],
        "before_cancel": [
            "raplbaddi.overrides.delivery_note.before_cancel",
        ],
        "on_cancel": [
            "raplbaddi.overrides.delivery_note.on_cancel",
        ],
        "on_update_after_submit": [
            "raplbaddi.overrides.delivery_note.on_update_after_submit",
        ],
    },
    "Sales Order": {
        "validate": [
            "raplbaddi.overrides.sales_order.validate",
        ],
    },
    "Purchase Order": {
        "before_insert": [
            "raplbaddi.overrides.purchase_order.before_insert",
        ],
        "validate": [
            "raplbaddi.overrides.purchase_order.validate",
        ],
    },
    "Purchase Receipt": {
        "before_insert": [
            "raplbaddi.overrides.purchase_receipt.before_insert",
        ],
        "validate": [
            "raplbaddi.overrides.purchase_receipt.validate",
        ],
    },
    "Employee": {
        "autoname": [
            "raplbaddi.overrides.employee.autoname",
        ],
        "validate": [
            "raplbaddi.overrides.employee.validate",
        ],
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "crons": {
    #     "0 0 1 1 *": [
    #         "raplbaddi.jobs.salary.yearly",    
    #     ],
    # },
# 	"all": [
# 		"raplbaddi.tasks.all"
# 	],
# 	"daily": [
# 		"raplbaddi.tasks.daily"
# 	],
# 	"hourly": [
# 		"raplbaddi.tasks.hourly"
# 	],
# 	"weekly": [
# 		"raplbaddi.tasks.weekly"
# 	],
# 	"monthly": [
# 		"raplbaddi.tasks.monthly"
# 	],
}

# Testing
# -------

# before_tests = "raplbaddi.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "raplbaddi.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "raplbaddi.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["raplbaddi.utils.before_request"]
# after_request = ["raplbaddi.utils.after_request"]

# Job Events
# ----------
# before_job = ["raplbaddi.utils.before_job"]
# after_job = ["raplbaddi.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"raplbaddi.auth.validate"
# ]


override_whitelisted_methods = {
    "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note": "raplbaddi.overrides.make_delivery_note"
}

export_python_type_annotations = True

fixtures = ["Custom Field", "Custom DocPerm", "Client Script"]

website_route_rules = [
    {"from_route": "/customer_support/<path:app_path>", "to_route": "customer_support"},
]
