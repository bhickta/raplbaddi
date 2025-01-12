frappe.ui.form.on('IssueRapl', {
    setup(frm) {
        get_google_api_key(frm);
        add_elements();
    },
    refresh: function (frm) {
        add_buttons(frm);
    },
	after_save: function(frm) {
		$('#places-input').val('')
	}
});


function add_elements() {
    $("#form-tabs").append("<input type='text' id='places-input' style='width: 700px; height: 40px;'>");
}

function get_google_api_key(frm) {
    frappe.db.get_single_value('Google Settings', 'api_key')
        .then(r => {
            LoadScript(r, frm);
        });
}

function LoadScript(api_key, frm) {
    let script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${api_key}&libraries=places`;
    script.async = true;
    script.defer = true;

    script.addEventListener('load', function () {
        frappe.google = new google.maps.places.Autocomplete(document.getElementById('places-input'), {componentRestrictions: { country: "in" }});
        frappe.google.addListener('place_changed', function () {
            frm.selectedPlace = frappe.google.getPlace();
			frm.set_value('customer_address', frm.selectedPlace.formatted_address)
			let state = ""
			frm.selectedPlace.address_components.forEach( r => {
				if(r.types.includes("administrative_area_level_1")) {
					state = r.long_name
				}
			})
			frm.set_value('customer_address', frm.selectedPlace.formatted_address)
			frm.set_value('customer_address_state', state)
			frm.set_value('latitude', frm.selectedPlace.geometry.location.lat())
			frm.set_value('longitude', frm.selectedPlace.geometry.location.lng())
        });
    });

    document.head.appendChild(script);
}


// Custom Buttons
function add_buttons(frm) {
	frm.add_custom_button(__('Select SC'), function () {
		frm.call({
			method: 'get_addresses',
			doc: frm.doc,
			callback: function (response) {
				if (response.message) {
					var options = response.message;
					frappe.prompt({
						label: __('Select an Address'),
						fieldname: 'selected_address',
						fieldtype: 'Select',
						options: options,
						reqd: 1,
					},
						(values) => {
							var value = values.selected_address.split(':');
							frm.set_value('service_centre', value[0]);
							frm.set_value('aerial_kilometer', 2 * parseFloat(value[1]));
                            frm.call({
                                method: 'set_kilometers',
                                doc: frm.doc,
                                args: {
                                    service_centre: value[0]
                                },
                                callback: function(response) {
                                    frm.refresh()
                                }
                            })
						});
				}
			}
		});
	});
}