/*
Lesson 3,
Subject: client/server communication
Date and time: Wednesday 26th of February 2014. 10:15-12 am.
Location: S26 C building, Campus Valla.
Author: Sahand Sadjadee

Revised version.
*/

// New search and store functions which make calls to 'getcontact' and 'addcontact' server functions respectively instead of using 'serverstub.js' as it was done in lesson 1.
 


//new store method
var store = function(formData){
     // The HTTP method and server function URL is specified in the HTML form and accessible via the formData object.
     // Here, The POST method is used for sending data to the server.

    var con = new XMLHttpRequest();
    
    //Defining a call back which is called as soon as the result arrives from the server
    con.onreadystatechange=function(event){
        // Checking if nothing has gone wrong at the server and the request has been processed
        if (event.target.readyState==4 && event.target.status==200){
            // It is assumed that the server returns the result in JSON format 
            var response = JSON.parse(event.target.responseText);


            var message = document.getElementById("message");

            // It is assumed that the returned data has a field named 'message'
            message.innerHTML = response.message;
        }
    }

    con.open(formData.method,formData.action, true);
    con.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    con.send("firstname=" + formData.firstname.value + "&familyname=" + formData.familyname.value + "&phonenumber=" +      
    formData.phonenumber.value);

    return false;   

}


//New search method
var search = function(formData){
     // The HTTP method and server function URL is specified in the HTML form and accessible via the formData object.
     // Here, The GET method is used for sending data to the server.

    var con = new XMLHttpRequest();

    //Defining a call back which is called as soon as the result arrives from the server    
    con.onreadystatechange=function(event){
       // Checking if nothing has gone wrong at the server and the request has been processed
        if (event.target.readyState==4 && event.target.status==200){
            var result = document.getElementById("result");

            // It is assumed that the server returns the result in JSON format 
            var response = JSON.parse(event.target.responseText);

            // It is assumed that the returned data has a field named 'result' which indicates if there is a match or not.
            if ( response.result == "true"){
               // It is assumed that the returned data has a field named 'data' which contains the whole information about the found contact.
               result.innerHTML =  response.data.firstname + " " +response.data.familyname + " " +      
               response.data.phonenumber;
            }else
                result.innerHTML =  response.message;
         }
    }

    con.open(formData.method,formData.action + "?firstname=" + formData.firstname.value + "&familyname=" + formData.familyname.value , true);
    con.send(null);

    return false;
}


