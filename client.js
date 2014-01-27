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

validateSignUp = function(formData) {
    return true;
};


