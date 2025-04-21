let deliveredToggleCount = 1;

frappe.ui.form.on('Sales Order', {
  onload(frm) {
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button(__('Toggle Delivered'), () => {
        frm.doc.items.forEach((row, idx) => {
          if (row.qty <= row.delivered_qty) {
            const itemRow = $(`[data-idx='${idx + 1}']`);
            deliveredToggleCount % 2 ? itemRow.hide() : itemRow.show();
          }
        });
        deliveredToggleCount++;
      });
    }

    if (frm.doc.customer) {
      setShippingAddressQuery(frm);
    }

    if (frm.doc.docstatus === 1 && frappe.user.name === 'kumarom906@gmail.com' && frm.doc.conditions) {
      frappe.warn('These are the Remarks', frm.doc.conditions, () => { }, 'Continue', true);
    }

    if (!frm.doc.customer && frm.doc.delivery_date && frm.doc.no_delivery_date) {
      frm.set_value('delivery_date', frappe.datetime.year_end());
    }
  },

  refresh(frm) {
    frm.events.queries(frm);
  },
  queries(frm) {
    frm.set_query("billing_rule", function () {
      return {
        query: "raplbaddi.controllers.queries.billing_rule",
        filters: {
          applicable_for: ["in", ["Selling", "Both"]],
        },
      };
    });
  },

  before_save(frm) {
    let zeroDiscountItems = [];

    frm.doc.items.forEach(item => {
      frappe.model.set_value(item.doctype, item.name, 'warehouse', item.name_of_brand + ' - RAPL');
      frappe.model.set_value(item.doctype, item.name, 'delivery_date', frm.doc.delivery_date);
      frappe.model.set_value(item.doctype, item.name, 'discount_amount', Math.round(item.discount_amount));
      frappe.model.set_value(item.doctype, item.name, 'rate', Math.round(item.rate));

      if (item.rate <= 0) {
        frappe.throw(`Rate of ${item.item_code} should not be 0`);
      }
      if (item.brand === 'Red Star' && /K(WT?|BH)?$/.test(item.item_code)) {
        frappe.throw('Red Star Brand cannot be selected in Kiya Models');
      }
      if (!item.custom_box) {
        frappe.model.set_value(item.doctype, item.name, 'custom_box', 'Any Plain');
      }
      if (item.discount_amount <= 0) {
        zeroDiscountItems.push(`${item.item_code} - ${item.name_of_brand}`);
      }
    });

    if (zeroDiscountItems.length) {
      frappe.warn('Possible Wrong Discounts', zeroDiscountItems.join('\n'));
    }
  },

  after_save(frm) {
    if (!frm.doc.shipping_address_name) {
      frm.set_value('shipping_address_name', frm.doc.customer_address);
      frm.refresh_field('shipping_address_name');
    }
  },

  before_submit(frm) {
    frm.set_value('submission_date', frappe.datetime.now_date());
  },

  before_cancel(frm) {
    frm.events.ask_for_reason_of_cancellation(frm);
  },
  ask_for_reason_of_cancellation(frm) {
    let dialog = new frappe.ui.Dialog({
      title: __('Reason for Cancellation'),
      fields: [{ fieldname: 'reason_for_cancellation', fieldtype: 'Text', reqd: 1 }],
      primary_action: () => {
        let data = dialog.get_values();
        frappe.call({
          method: 'frappe.desk.form.utils.add_comment',
          args: {
            reference_doctype: frm.doctype,
            reference_name: frm.docname,
            content: __('Reason for Cancellation:') + ' ' + data.reason_for_cancellation,
            comment_email: frappe.session.user,
            comment_by: frappe.session.user_fullname
          },
          callback(r) {
            if (!r.exc) dialog.hide();
          }
        });
      }
    });
    dialog.show();
  }
});

frappe.ui.form.on('Sales Order Item', {
  items_add(frm, cdt, cdn) {
    copyPrevious(frm, locals[cdt][cdn], ['name_of_brand']);
  },
  qty(frm, cdt, cdn) {
    copyPrevious(frm, locals[cdt][cdn], ['discount_amount']);
  },
  name_of_brand(frm, cdt, cdn) {
    updateCustomBox(frm, cdt, cdn);
  },
  item_code(frm, cdt, cdn) {
    updateCustomBox(frm, cdt, cdn);
  },
  plain_type(frm, cdt, cdn) {
    let row = frm.get_field('items').grid.get_row(cdn).doc;
    if (row.box_type === 'Printed') {
      frappe.model.set_value(cdt, cdn, 'plain_type', '');
      frappe.show_alert('Set Either - Printed Or Plain Type');
    }
  }
});

function copyPrevious(frm, row, fields) {
  let items = frm.doc.items;
  if (items.length > 1 && row.idx > 1) {
    fields.forEach(field => {
      let prev = items[row.idx - 2][field];
      frappe.model.set_value(row.doctype, row.name, field, prev);
    });
  }
}

function updateCustomBox(frm, cdt, cdn) {
  let row = locals[cdt][cdn];
  if (!row.item_code || !row.name_of_brand) return;
  frappe.call({
    method: "raplbaddi.overrides.sales_order.update_custom_box_backend",
    args: {
      item_code: row.item_code,
      name_of_brand: row.name_of_brand,
      cdt: cdt,
      cdn: cdn
    },
    callback: function(r) {
      if (!r.exc) {
        frappe.model.set_value(cdt, cdn, 'custom_box', r.message.custom_box);
        frm.refresh_field('custom_box');
      } else {
        console.error("Error in backend function:", r.exc);
      }
    }
  });
}

function setShippingAddressQuery(frm) {
  frm.set_query('shipping_address_name', () => ({ filters: {} }));
}