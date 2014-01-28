window.onload = function() {
    displayView();
    // TODO Error when logged, when signUpForm "doesn't exist"
    defaultBorder = document.signUpForm.elements[0].style.border;
};

displayView = function() {
    var view
    if(localStorage.token != null) {
        view = document.getElementById("profileview");
    } else {
        view = document.getElementById("welcomeview");
    }
    document.getElementById("view").innerHTML = view.innerHTML;
};

submitLogin = function(formData) {
    console.log("Validating... ");
    if(validateSignIn(formData)) {
        console.log("Complete.");
        var result = serverstub.signIn(formData.signInEmail.value, formData.signInPassword.value);
        if(result.success) {
            localStorage.token = result.data;
            location.reload();
        } else {
            document.getElementById("sign-in-message").innerHTML = result.message;
            formData.signInEmail.style.borderColor = "red"
        }
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

        var dataObject = new Object();
        dataObject.email = formData.email.value;
        dataObject.password = formData.password.value;
        dataObject.firstname = formData.fname.value;
        dataObject.familyname = formData.lname.value;
        dataObject.gender = formData.gender.value;
        dataObject.city = formData.city.value;
        dataObject.country = formData.country.value;

        var result = serverstub.signUp(dataObject);
        document.getElementById("sign-up-message").innerHTML = result.message;

        if(result.success) {
            clearSignUpForm(formData);
        } else {
            formData.email.style.borderColor = "red"
        }

    } else {
        console.log("User fucked up.");
    }
};

validateSignUp = function(formData) {

    var okay = true;
    var form = document.signUpForm;
    for(i = 0; i < form.elements.length - 1 ; i++) {
        if(form.elements[i].value == "") {
            okay = false;
            form.elements[i].style.borderColor = "red";
        }
    }

    if(formData.password.value != formData.password2.value) {
        okay = false;
        formData.password.style.borderColor = "red";
        formData.password2.style.borderColor = "red";
    }

    return okay;
};

clearSignUpForm = function(formData) {
    formData.email.value = "";
    formData.password.value = "";
    formData.password2.value = "";
    formData.fname.value = "";
    formData.lname.value = "";
    formData.gender.selectedIndex = 0;
    formData.city.value = "";
    formData.country.value = "";
}

clearErrorBorder = function(element) {
    // TODO Prettier solution? defaultBorder is declared in onLoad...
    element.style.border = defaultBorder;

    if(element.name == "email") {
        document.getElementById("sign-up-message").innerHTML = "";
    } else if(element.name == "signInEmail") {
        document.getElementById("sign-in-message").innerHTML = "";
    }
}