from erpnext.controllers.queries import get_fields, get_filters_cond, get_match_cond, frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def billing_rule(doctype, txt, searchfield, start, page_len, filters):
	doctype = "Billing Rule Rapl"
	conditions = []
	fields = get_fields(doctype, ["name"])

	return frappe.db.sql(
		"""select {fields}
		from `tabBilling Rule Rapl`
		where `tabBilling Rule Rapl`.disabled=0
			and `tabBilling Rule Rapl`.`{key}` like %(txt)s
			{fcond} {mcond}
		order by
			(case when locate(%(_txt)s, name) > 0 then locate(%(_txt)s, name) else 99999 end),
			idx desc, name
		limit %(page_len)s offset %(start)s""".format(
			fields=", ".join(fields),
			fcond=get_filters_cond(doctype, filters, conditions).replace("%", "%%"),
			mcond=get_match_cond(doctype).replace("%", "%%"),
			key=searchfield,
		),
		{
			"txt": "%" + txt + "%",
			"_txt": txt.replace("%", ""),
			"start": start or 0,
			"page_len": page_len or 20,
		},
	)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def issue_type(doctype, txt, searchfield, start, page_len, filters):
    doctype = "Issue Type"
    conditions = []
    fields = get_fields(doctype, ["name"])

    return frappe.db.sql(
        """SELECT `tabIssue Type`.name, 
                  IFNULL(issue_count.count, 0) AS occurrence_count
        FROM `tabIssue Type`
        LEFT JOIN (
            SELECT issue_type, COUNT(*) AS count
            FROM `tabIssueRapl Item`
            GROUP BY issue_type
        ) AS issue_count 
        ON issue_count.issue_type = `tabIssue Type`.name
        WHERE `tabIssue Type`.is_disabled = 0
            AND `tabIssue Type`.`{key}` LIKE %(txt)s
            {fcond} {mcond}
        ORDER BY occurrence_count DESC,
                 (CASE WHEN LOCATE(%(_txt)s, `tabIssue Type`.name) > 0 THEN LOCATE(%(_txt)s, `tabIssue Type`.name) ELSE 99999 END),
                 idx DESC, `tabIssue Type`.name
        LIMIT %(page_len)s OFFSET %(start)s""".format(
            fcond=get_filters_cond(doctype, filters, conditions).replace("%", "%%"),
            mcond=get_match_cond(doctype).replace("%", "%%"),
            key=searchfield,
        ),
        {
            "txt": "%" + txt + "%",
            "_txt": txt.replace("%", ""),
            "start": start or 0,
            "page_len": page_len or 20,
        },
    )

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def sub_issue(doctype, txt, searchfield, start, page_len, filters):
    doctype = "Sub Issue"
    conditions = []
    fields = get_fields(doctype, ["name"])

    return frappe.db.sql(
        """SELECT `tabSub Issue`.name, 
                  IFNULL(sub_issue_count.count, 0) AS occurrence_count
        FROM `tabSub Issue`
        LEFT JOIN (
            SELECT sub_issue, COUNT(*) AS count
            FROM `tabIssueRapl Item`
            GROUP BY sub_issue
        ) AS sub_issue_count 
        ON sub_issue_count.sub_issue = `tabSub Issue`.name
        WHERE `tabSub Issue`.is_disabled = 0
            AND `tabSub Issue`.`{key}` LIKE %(txt)s
            {fcond} {mcond}
        ORDER BY occurrence_count DESC,
                 (CASE WHEN LOCATE(%(_txt)s, `tabSub Issue`.name) > 0 THEN LOCATE(%(_txt)s, `tabSub Issue`.name) ELSE 99999 END),
                 idx DESC, `tabSub Issue`.name
        LIMIT %(page_len)s OFFSET %(start)s""".format(
            fcond=get_filters_cond(doctype, filters, conditions).replace("%", "%%"),
            mcond=get_match_cond(doctype).replace("%", "%%"),
            key=searchfield,
        ),
        {
            "txt": "%" + txt + "%",
            "_txt": txt.replace("%", ""),
            "start": start or 0,
            "page_len": page_len or 20,
        },
    )
