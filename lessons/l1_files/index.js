var phonebook = null;

if(localStorage.getItem("phonebook") == null)
    phonebook = new Object();
else phonebook = JSON.parse(localStorage.getItem("phonebook"));


var persist = function(){
    localStorage.setItem("phonebook", JSON.stringify(phonebook));
}

var store = function(formData){

    var firstname = formData.firstname.value;;
    var familyname = formData.familyname.value;
    var phonenumber =  formData.phonenumber.value;
    if(firstname.trim() != "" && familyname.trim() != "" && phonenumber.trim() != ""){
        var contact ={
            "firstname": firstname,
            "familyname": familyname,
            "phonenumber": phonenumber
        }
        if(phonebook[firstname.concat(familyname)] == undefined)
           phonebook[firstname.concat(familyname)] = contact;
        else alert("contact exists!"); // using alert is not the best solution. you will be guided to use another approach in your Twidder project.
        persist();
    }else{
        alert("fill in all the fields"); // using alert is not the best solution. you will be guided to use another approach in your Twidder project.
    }

}

window.onload = function(){
    // no use here!
}

var search = function(formData){
    var firstname = formData.firstname2.value;;
    var familyname = formData.familyname2.value;
    if(firstname.trim() != "" && familyname.trim() != ""){
         if (phonebook[firstname.concat(familyname)] == undefined){
             alert("contact does not exist!") // using alert is not the best solution. you will be guided to use another approach in your Twidder project.
         }else{
             var r = document.getElementById("result");
             var contact = phonebook[firstname.concat(familyname)];
             r.innerHTML = contact.firstname + " " + contact.familyname + " " + contact.phonenumber;
         }
    }else{
        alert("fill in all the fields"); // using alert is not the best solution. you will be guided to use another approach in your Twidder project.
    }

}
