frappe.ready(() => {
    get_global_variables();
    setup_timezone_selector();
});

function get_global_variables() {
    window.timezones = ["Geyser", "Cooler"];
}

function setup_timezone_selector() {
    let timezones_element = document.getElementById('appointment-timezone');
    window.timezones.forEach(timezone => {
        let opt = document.createElement('option');
        opt.value = timezone;
        opt.innerHTML = timezone;
        timezones_element.appendChild(opt);
    });

    console.log('Timezone Selector Set up');
}