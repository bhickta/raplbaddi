// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on('PB Creation Tool', {
    onload(frm) {
        frm.set_query('box_type', () => {
            return {
                filters: [
                    ['name', 'in', ['Brand', 'Plain Box Type']]
                ]
            };
        });
    },
    validate(frm){
        frm.doc.items.forEach((e) =>{
            if(e.paper) {
                frappe.db.exists('Item', e.paper).then(r => {
                    console.log(r)
                    if(!r) {
                        e.paper = ''
                        frm.refresh_field('items', 'paper')
                    }
                })
            }
            })
    },

    box_particular(frm) {
        frappe.db.get_doc(frm.doc.box_type, frm.doc.box_particular).then(r => frm.set_value('paper_names', r.paper_names))
        frm.refresh_field('paper_names')
    },
    create_box(frm) {
        frm.doc.items = []
        create_box(frm)
    }
});


async function create_box(frm) {
    try {
        for (let paper_name of frm.doc.paper_names) {
            const { items } = await frappe.db.get_doc('Paper Name', paper_name.title);
            const newItemList = items.map(item => ({
                'box': `PB${item.capacity}${item.model.slice(0, 1)} ${frm.doc.box_particular}`,
                'paper': `PP ${frm.doc.box_particular} ${paper_name.title}`,
                'model': item.model,
                'capacity': item.capacity,
                'paper_type': paper_name.paper_type,
                'paper_name': paper_name.title
            }));

            const mergedItems = [...frm.doc.items, ...newItemList]
                .filter((item, index, self) =>
                    index === self.findIndex(i =>
                        i.model === item.model &&
                        i.capacity === item.capacity &&
                        i.paper_type === item.paper_type &&
                        i.paper_name === item.paper_name
                    )
                )
            frm.set_value('items', mergedItems);
            frm.refresh_field('items');
            frm.set_value('paper_names', '')
        }
    } catch (error) {
        console.error('An error occurred:', error);
    }
}
