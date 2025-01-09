# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

from raplbaddi.raplbaddi.report.accounts_receivable_rapl.accounts_receivable_rapl import ReceivablePayableReport


def execute(filters=None):
	args = {
		"account_type": "Payable",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return ReceivablePayableReport(filters).run(args)
