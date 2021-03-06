window.onload = function() {

    if(localStorage.token != null) {
        var userData = serverstub.getUserDataByToken(localStorage.token).data;
        displayView(userData);
        localStorage.currentUserView = userData.email;
    } else {
        displayView();
    }

    // TODO Find more elegant solution for the "default border"
    if(document.getElementById("signup-email") != null) {
        defaultBorder = document.signUpForm.elements[0].style.border;
    } else if(document.getElementById("oldPassword") != null) {
        defaultBorder = document.getElementById("oldPassword").style.border;
    }
};

/**
 * Displays given "welcomeview" or "profileview" depending on if token is set
 * @param userData (optional) Needed with "profileview"
 */
displayView = function(userData) {
    if(localStorage.token != null) {
        document.getElementById("view").innerHTML = document.getElementById("profileview").innerHTML;
        populateBio(userData);
        reloadWall(userData.email);
    } else {
        document.getElementById("view").innerHTML = document.getElementById("welcomeview").innerHTML;
    }
};

/**
 * Submits sign in to the server if input passes validation.
 * @param formData The signInForm
 */
submitLogin = function(formData) {
    if(validateSignIn(formData)) {
        var result = serverstub.signIn(formData.signInEmail.value, formData.signInPassword.value);
        if(result.success) {
            localStorage.token = result.data;
            var userData = serverstub.getUserDataByToken(result.data).data;
            localStorage.currentUserView = userData.email;
            displayView(userData);
        } else {
            document.getElementById("sign-in-message").innerHTML = result.message;
            formData.signInEmail.style.borderColor = "red"
        }
    }
};


/**
 * Validates sign in form
 * @param formData The signInForm
 * @returns {boolean} false if email or password is empty, else true
 */
validateSignIn = function(formData) {
    var email = formData.signInEmail.value;
    var password = formData.signInPassword.value;

    return email.trim() != "" && password != "";
};


/**
 * Submits sign up to server if user input passes validation.
 * @param formData The signUpForm.
 */
submitSignUp = function(formData) {

    if(validateSignUp(formData)) {

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

    }
};


/**
 * Validates the signUpForm.
 * @param formData The signUpForm
 * @returns {boolean} false if a element is empty or password and retype doesn't match
 */
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

/**
 * Clears the signUpForm.
 * @param formData The signUpForm
 */
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

/**
 * Uses the globally defined defaultBorder for reseting borders on given element.
 * @param element The element which borders are to be cleared on
 */
clearErrorBorder = function(element) {
    // TODO Prettier solution? defaultBorder is declared in onLoad...
    element.style.border = defaultBorder;

    if(element.name == "email") {
        document.getElementById("sign-up-message").innerHTML = "";
    } else if(element.name == "signInEmail") {
        document.getElementById("sign-in-message").innerHTML = "";
    }
};

/**
 * Select which tab to be visible in the profileview.
 * @param index 0 displays home, 1 displays browse and 2 displays account tab
 */
tabSelect = function(index) {
    if(index == 0) {
        document.getElementById("home").style.display = "block";
        document.getElementById("browse").style.display = "none";
        document.getElementById("account").style.display = "none";
        // Get data of logged in user
        var result = serverstub.getUserDataByToken(localStorage.token);
        populateBio(result.data);
        reloadWall(result.data.email);
        localStorage.currentUserView = result.data.email;
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

/**
 * Submits password change to server if new password passes validation.
 * @param formData The form
 */
submitChangePassword = function(formData) {

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

        // Callback for removing the message after a couple of seconds
        var callback = function() {
            document.getElementById("changePasswordMessage").innerHTML = "";
        };
        setTimeout(callback, 8000);

    }
};

/**
 * Validates the change password form.
 * @param formData The form.
 * @returns {boolean} false if newPassword != newPassword2 (the retype)
 */
validateChangePassword = function(formData) {
    if(formData.newPassword.value != formData.newPassword2.value) {
        formData.newPassword.style.borderColor = "red";
        formData.newPassword2.style.borderColor = "red";
        return false;
    }
    return true;
};

/**
 * Signs out the user on the server and removes local token and userData
 */
submitSignOut = function() {
    serverstub.signOut(localStorage.token);
    localStorage.removeItem("token");
    localStorage.removeItem("currentUserView");
    location.reload();
};

/**
 * Populates the bio-element with user data.
 * @param userData As given by serverstyb.getUserDataByToken(localStorage.token).data or the like
 */
populateBio = function(userData) {
    var text = userData.firstname + " " + userData.familyname + "<br/>" +
        userData.gender + " from " + userData.city + ", " + userData.country +
        "<br/><a href='mailto:" + userData.email + "'>" +
        userData.email + "</a>";

    document.getElementById("bio").innerHTML = text;
};


/**
 * Posts a message to the user as defined by localStorage.currentUserView.
 * @param formData
 */
submitPostMessage = function(formData) {

    var result;
    if(localStorage.currentUserView === undefined) {
        result = serverstub.postMessage(localStorage.token, formData.message.value, serverstub.getUserDataByToken(localStorage.token));
    } else {
        result = serverstub.postMessage(localStorage.token, formData.message.value, localStorage.currentUserView);
    }

    if(result.success) {
        formData.message.value = "";
        reloadWall(localStorage.currentUserView);
    }

    document.getElementById("postMessageResultMessage").innerHTML = result.message;

    // Callback for removing the message after a couple of seconds
    var callback = function() {
        document.getElementById("postMessageResultMessage").innerHTML = "";
    };
    setTimeout(callback, 8000);

};

/**
 * Fetches messages for the wall and puts them in the #messageArea. If the email paramter is omitted, the currently
 * signed in users' messages will be fetched.
 * @param email (optional) The email of the user for which you want to fetch messages from.
 */
reloadWall = function(email) {

    var result;
    if(email === undefined) {
        result = serverstub.getUserMessagesByEmail(localStorage.token, localStorage.currentUserView);
    } else {
        result = serverstub.getUserMessagesByEmail(localStorage.token, email);
    }

    if(result.success) {
        document.getElementById("messageArea").innerHTML = result.data.length > 0 ? "" : "<h2>No messages yet... ='(</h2>";
        for(i = 0 ; i < result.data.length ; i++) {
            document.getElementById("messageArea").innerHTML += generateMessage(result.data[i]);
        }
    }
};

/**
 * Generate a message for the stream with given data.
 * @param message A single message as provided by serverstub.getUserMessagesByToken() (or similar methods).
 * @returns {string} HTML for a stream message.
 */
generateMessage = function(message) {
    return "<div class='wallMessage'><h2>" + message.writer + " wrote...</h2><br/>"
        + message.content + "</div>";
};

/***
 * Fetches the profileview of the given user.
 * @param formData
 */
submitBrowse = function(formData) {
    var email = formData.browseEmail.value;
    var callback = function() {
        document.getElementById("browseMessage").innerHTML = "";
    };

    if(email != "") {
        var result = serverstub.getUserDataByEmail(localStorage.token, email);
        if(result.success) {
            localStorage.currentUserView = result.data.email;
            displayView(result.data);
        } else {
            document.getElementById("browseMessage").innerHTML = result.message;
            setTimeout(callback, 8000);
        }
    } else {
        document.getElementById("browseMessage").innerHTML = "You have to fill in an email!";
        document.getElementById("browseMessage").style.borderColor = "red";
        setTimeout(callback, 8000);
    }
};
