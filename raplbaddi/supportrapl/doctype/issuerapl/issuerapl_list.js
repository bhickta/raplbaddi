// frappe.listview_settings['IssueRapl'] = {
//     onload: function (listview) {
//         listview.page.add_menu_item(__("Calculate Amounts"), function () {
//             frappe.call({
//                 method: 'raplbaddi.supportrapl.doctype.issuerapl.issuerapl.set_rates',
//                 callback: function (response) {
//                     frappe.throw('Amounts has been calcualted')
//                 }
//             })
//         });
//     }
// }