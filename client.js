window.onload = function() {
    displayView();
};

displayView = function() {
    var welcomeView = document.getElementById("welcomeview");
    document.getElementById("view").innerHTML = welcomeView.innerHTML;
};

submitLogin = function(formData) {
    console.log("Validating... ");
    if(validateSignIn(formData)) {
        console.log("Complete.");
    } else {
        console.log("User fucked up.");
    }
};

validateSignIn = function(formData) {
    var email = formData.signInEmail.value;
    var password = formData.signInPassword.value;

    return email.trim() != "" && password != "";
};

submitSignUp = function(formData) {
    console.log("Validating... ");
    if(validateSignUp(formData)) {
        console.log("Complete.");
    } else {
        console.log("User fucked up.");
    }
};

validateSignUp = function(formData) {
    var email = formData.email.value;
    var password = formData.password.value;
    var password2 = formData.password2.value;
    var fname = formData.fname.value;
    var lname = formData.lname.value;
    var gender = formData.gender.value;
    var city = formData.city.value;
    var country = formData.country.value;

    return (email != "") && (password != "") && (password2 != "") && (fname != "") && (lname != "") && (gender != "") && (city != "") && (password === password2);
};