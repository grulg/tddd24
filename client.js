window.onload = function() {
    displayView();

    // TODO Find more elegant solution for the "default border"
    if(document.getElementById("signup-email") != null) {
        defaultBorder = document.signUpForm.elements[0].style.border;
    } else if(document.getElementById("oldPassword") != null) {
        defaultBorder = document.getElementById("oldPassword").style.border;
    }
};

displayView = function() {
    if(localStorage.token != null) {
        document.getElementById("view").innerHTML = document.getElementById("profileview").innerHTML;
        var userData = serverstub.getUserDataByToken(localStorage.token).data;
        localStorage.userData = userData;
        populateBio(userData);
        reloadWall();
    } else {
        document.getElementById("view").innerHTML = document.getElementById("welcomeview").innerHTML;
    }
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
};

clearErrorBorder = function(element) {
    // TODO Prettier solution? defaultBorder is declared in onLoad...
    element.style.border = defaultBorder;

    if(element.name == "email") {
        document.getElementById("sign-up-message").innerHTML = "";
    } else if(element.name == "signInEmail") {
        document.getElementById("sign-in-message").innerHTML = "";
    }
};

tabSelect = function(index) {
    if(index == 0) {
        document.getElementById("home").style.display = "block";
        document.getElementById("browse").style.display = "none";
        document.getElementById("account").style.display = "none";
    } else if(index == 1) {
        document.getElementById("home").style.display = "none";
        document.getElementById("browse").style.display = "block";
        document.getElementById("account").style.display = "none";
    } else if(index == 2) {
        document.getElementById("home").style.display = "none";
        document.getElementById("browse").style.display = "none";
        document.getElementById("account").style.display = "block";
    }
};

submitChangePassword = function(formData) {
    console.log("Validating...");
    if(validateChangePassword(formData)) {

        var result = serverstub.changePassword(localStorage.token, formData.oldPassword.value, formData.newPassword.value);
        document.getElementById("changePasswordMessage").innerHTML = result.message;
        if(result.success) {
            formData.oldPassword.value = "";
            formData.newPassword.value = "";
            formData.newPassword2.value = "";
        } else {
            formData.oldPassword.value = "";
            formData.oldPassword.style.borderColor = "red";
        }

    } else {
        console.log("User fucked up.");
    }
};

validateChangePassword = function(formData) {
    if(formData.newPassword.value != formData.newPassword2.value) {
        formData.newPassword.style.borderColor = "red";
        formData.newPassword2.style.borderColor = "red";
        return false;
    }
    return true;
};

submitSignOut = function() {
    serverstub.signOut(localStorage.token);
    localStorage.removeItem("token");
    localStorage.removeItem("userData");
    location.reload();
};

populateBio = function(userData) {
    var text = userData.firstname + " " + userData.familyname + "<br/>" +
        userData.gender + " from " + userData.city + ", " + userData.country +
        "<br/><a href='mailto:" + userData.email + "'>" +
        userData.email + "</a>";

    document.getElementById("bio").innerHTML = text;
};


submitPostMessage = function(formData) {
    var callback = function() {
        document.getElementById("postMessageResultMessage").innerHTML = "";
    };

    var result = serverstub.postMessage(localStorage.token, formData.message.value, localStorage.userData.email);
    document.getElementById("postMessageResultMessage").innerHTML = result.message;
    setTimeout(callback, 8000);
    if(result.success) {
        formData.message.value = "";
        reloadWall();
    }
};

reloadWall = function() {
    console.log("Fetching messages...");
    var result = serverstub.getUserMessagesByToken(localStorage.token);
    if(result.success) {
        console.log("Success!");
        document.getElementById("messageArea").innerHTML = "";
        for(i = 0 ; i < result.data.length ; i++) {
            document.getElementById("messageArea").innerHTML += generateMessage(result.data[i]);
        }
    }
};

generateMessage = function(message) {
    return "<div class='streamMessage'><h2>" + message.writer + " wrote...</h2><br/>"
        + message.content + "</div>";
};