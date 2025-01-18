class GoogleMapsIntegration {
    constructor(apiKey, country = "in") {
        this.apiKey = apiKey;
        this.country = country;
        this.autocomplete = null;
    }

    // Load Google Maps script dynamically
    loadScript(callback) {
        if (!document.querySelector('script[src*="maps.googleapis.com/maps/api/js"]')) {
            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key=${this.apiKey}&libraries=places`;
            script.async = true;
            script.defer = true;

            script.addEventListener('load', () => {
                console.log('Google Maps script loaded.');
                if (callback) callback();
            });
            script.addEventListener('error', () => {
                frappe.msgprint(__('Failed to load Google Maps API script.'));
            });

            document.head.appendChild(script);
        } else {
            if (callback) callback();
        }
    }

    // Initialize Autocomplete for a given input element
    initializeAutocomplete(inputElementId, onPlaceChanged) {
        if (!google || !google.maps || !google.maps.places) {
            frappe.msgprint(__('Google Maps API is not loaded yet.'));
            return;
        }

        const inputElement = document.getElementById(inputElementId);
        if (!inputElement) {
            frappe.msgprint(__('Input element not found.'));
            return;
        }

        this.autocomplete = new google.maps.places.Autocomplete(inputElement, {
            componentRestrictions: { country: this.country },
        });

        this.autocomplete.addListener('place_changed', () => {
            const place = this.autocomplete.getPlace();
            if (onPlaceChanged && typeof onPlaceChanged === "function") {
                onPlaceChanged(place);
            }
        });
    }
}

// Utility class for custom UI and form handling
class IssueRaplHandler {
    constructor(frm) {
        this.frm = frm;
        this.googleMaps = null;
    }

    // Initialize the handler
    initialize() {
        this.addInputField();
        this.setupGoogleMaps();
    }

    // Setup Google Maps integration
    setupGoogleMaps() {
        frappe.db.get_single_value('Google Settings', 'api_key').then(apiKey => {
            if (!apiKey) {
                frappe.msgprint(__('Google API Key is missing.'));
                return;
            }

            this.googleMaps = new GoogleMapsIntegration(apiKey);
            this.googleMaps.loadScript(() => {
                this.googleMaps.initializeAutocomplete('places-input', this.handlePlaceChanged.bind(this));
            });
        });
    }

    // Handle place selection and update form fields
    handlePlaceChanged(place) {
        if (!place.geometry) {
            frappe.msgprint(__('Selected place has no location data.'));
            return;
        }

        const addressComponents = place.address_components || [];
        const state = this.extractStateFromComponents(addressComponents);

        this.frm.set_value('customer_address', place.formatted_address);
        this.frm.set_value('customer_address_state', state);
        this.frm.set_value('latitude', place.geometry.location.lat());
        this.frm.set_value('longitude', place.geometry.location.lng());
    }

    // Extract the state from address components
    extractStateFromComponents(components) {
        let state = '';
        components.forEach(component => {
            if (component.types.includes("administrative_area_level_1")) {
                state = component.long_name;
            }
        });
        return state;
    }

    // Add input field for Google Places Autocomplete
    addInputField() {
        if (!document.getElementById('places-input')) {
            const inputHtml = "<input type='text' id='places-input' style='width: 700px; height: 40px;'>";
            $("#form-tabs").append(inputHtml);
        }
    }

    // Add custom buttons to the form
    addCustomButtons() {
        this.frm.add_custom_button(__('Select SC'), this.handleSelectSC.bind(this));
    }

    // Handle "Select SC" button click
    handleSelectSC() {
        this.frm.call({
            method: 'get_addresses',
            doc: this.frm.doc,
            callback: (response) => {
                if (response.message) {
                    this.promptAddressSelection(response.message);
                }
            },
        });
    }

    // Prompt user to select an address
    promptAddressSelection(options) {
        frappe.prompt({
            label: __('Select an Address'),
            fieldname: 'selected_address',
            fieldtype: 'Select',
            options: options,
            reqd: 1,
        }, (values) => {
            const [serviceCentre, distance] = values.selected_address.split(':');
            this.updateServiceCentreDetails(serviceCentre, distance);
        });
    }

    // Update Service Centre details and call server-side method
    updateServiceCentreDetails(serviceCentre, distance) {
        this.frm.set_value('service_centre', serviceCentre);
        this.frm.set_value('aerial_kilometer', 2 * parseFloat(distance));
    }

    // Reset the input field after saving the form
    resetInputField() {
        $('#places-input').val('');
    }
}

// Main Frappe Form Script
frappe.ui.form.on('IssueRapl', {
    setup(frm) {
        const issueHandler = new IssueRaplHandler(frm);
        issueHandler.initialize();
    },
    refresh(frm) {
        const issueHandler = new IssueRaplHandler(frm);
        issueHandler.addCustomButtons();
    },
    after_save(frm) {
        const issueHandler = new IssueRaplHandler(frm);
        issueHandler.resetInputField();
    },
});