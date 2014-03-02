// var ws;
window.onload = function() {

    if(localStorage.token != null) {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                var userData = JSON.parse(xmlhttp.responseText);
                displayView(userData.data);
                localStorage.currentUserView = userData.data.email;
            }
        };
        xmlhttp.open("POST", "/get_user_data_by_token", true);
        xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        xmlhttp.send("token=" + localStorage.token);
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
        
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                var result = JSON.parse(xmlhttp.responseText);
                if(result.success) {
                    localStorage.token = result.data;
                    var xmlhttp2 = new XMLHttpRequest();
                    xmlhttp2.onreadystatechange = function() {
                        if(xmlhttp2.readyState == 4 && xmlhttp2.status == 200) {
                            var userData = JSON.parse(xmlhttp2.responseText).data;
                            localStorage.currentUserView = userData.email;
                            displayView(userData);                    
                        }
                    };
                    xmlhttp2.open("POST", "/get_user_data_by_token", true);
                    xmlhttp2.setRequestHeader("Content-type","application/x-www-form-urlencoded");
                    xmlhttp2.send("token=" + localStorage.token);

                } else {                    
                    document.getElementById("sign-in-message").innerHTML = result.message;
                    formData.signInEmail.style.borderColor = "red"
                }    
            }
        };
        xmlhttp.open("POST", "/sign_in", true);
        xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        xmlhttp.send("email=" + formData.signInEmail.value + "&password=" + formData.signInPassword.value);
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

        var data = "email=" + formData.email.value;
        data += "&password=" + formData.password.value;
        data += "&firstname=" + formData.fname.value;
        data += "&lastname=" + formData.lname.value;
        data += "&gender=" + formData.gender.value;
        data += "&city=" + formData.city.value;
        data += "&country=" + formData.country.value;

        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            
                var result = JSON.parse(xmlhttp.responseText);
                document.getElementById("sign-up-message").innerHTML = result.message;

                if(result.success) {
                    clearSignUpForm(formData);
                } else {
                    formData.email.style.borderColor = "red"
                }
            }
        };
        xmlhttp.open("POST", "/sign_up", true);
        xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        xmlhttp.send(data);
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
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                var result = JSON.parse(xmlhttp.responseText);
                populateBio(result.data);
                reloadWall(result.data.email);
                localStorage.currentUserView = result.data.email;
            }
        };
        xmlhttp.open("POST", "/get_user_data_by_token", true);
        xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        xmlhttp.send("token=" + localStorage.token);
        
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

        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange =  function() {
            if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                var result = JSON.parse(xmlhttp.responseText);
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
        xmlhttp.open("POST", "/change_password", true);
        xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        xmlhttp.send("token=" + localStorage.token + "&old_password=" + 
            formData.oldPassword.value + "&new_password=" + formData.newPassword.value);
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
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var result = JSON.parse(xmlhttp.responseText);
            if(!result.success) {
                alert("Server said you weren't signed in... too bad!");
            }
            localStorage.removeItem("token");
            localStorage.removeItem("currentUserView");
            location.reload();    
        }
    };
    xmlhttp.open("POST", "/sign_out", true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send("token=" + localStorage.token);
};

/**
 * Populates the bio-element with user data.
 * @param userData As given by serverstyb.getUserDataByToken(localStorage.token).data or the like
 */
populateBio = function(userData) {
    var text = userData.firstname + " " + userData.lastname + "<br/>" +
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

    if("WebSocket" in window) {
        var credentials = {
            token: localStorage.token,
            email: localStorage.currentUserView,
            message: formData.message.value
        };
        
        ws = new WebSocket("ws://" + document.domain + ":5000/push_message");

        ws.onopen = function(event) {
            ws.send(JSON.stringify(credentials));
        }

        ws.onmessage = function(msg) {
            var result = JSON.parse(msg.data);
            if(result.success) {

                formData.message.value = "";
                generateWall(result.data);

            } else {
                alert("Couldn't post message.");
            }
            ws.close();
        }
    } else {
        alert("Websockets not supported, so this ain't gonna work!");
    }
};

/**
 * Fetches messages for the wall and puts them in the #messageArea. If the email paramter is omitted, the currently
 * signed in users' messages will be fetched.
 * @param email (optional) The email of the user for which you want to fetch messages from.
 */
reloadWall = function(email) {

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var result = JSON.parse(xmlhttp.responseText);
            if(result.success) {
                generateWall(result.data);
            } else {
                alert("Couldn't reload wall.");
            }
        }
    };
    xmlhttp.open("POST", "/get_user_messages_by_email", true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");

    if(email === undefined) {
        xmlhttp.send("token=" + localStorage.token + "&email=" + localStorage.currentUserView);
    } else {
        xmlhttp.send("token=" + localStorage.token + "&email=" + email);
    }
};

/**
 * Generates the wall based on the json data returned from the server.
 */
generateWall = function(data) {
    document.getElementById("messageArea").innerHTML = data.length > 0 ? "" : "<h2>No messages yet... ='(</h2>";
    for(i = 0 ; i < data.length ; i++) {
        document.getElementById("messageArea").innerHTML += generateMessage(data[i]);
    }
}

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
        
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                var result = JSON.parse(xmlhttp.responseText);
                if(result.success) {
                    localStorage.currentUserView = result.data.email;
                    displayView(result.data);
                } else {
                    document.getElementById("browseMessage").innerHTML = result.message;
                    setTimeout(callback, 8000);
                }
            }
        };
        xmlhttp.open("POST", "/get_user_data_by_email", true);
        xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        xmlhttp.send("token=" + localStorage.token + "&email=" + email);
        
    } else {
        document.getElementById("browseMessage").innerHTML = "You have to fill in an email!";
        document.getElementById("browseMessage").style.borderColor = "red";
        setTimeout(callback, 8000);
    }
};
