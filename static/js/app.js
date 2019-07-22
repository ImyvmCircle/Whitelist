document.querySelectorAll(".mdc-button").forEach(function(elem) {
    new mdc.ripple.MDCRipple(elem);
});

document.querySelectorAll(".mdc-text-field").forEach(function(elem) {
    new mdc.textField.MDCTextField(elem);
});

document.querySelectorAll(".mdc-radio").forEach(function(radio) {
    var elem = new mdc.formField.MDCFormField(radio.parentElement);
    var radio = new mdc.radio.MDCRadio(radio);
    elem.input = radio;
});

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2)
        return parts.pop().split(";").shift();
}
