let alterProfile = document.querySelector("#alterProfile");
let accountPrivateSet = document.querySelector("#accountPrivateSet");
let alterAccount = document.querySelector("#alterAccount");

alterProfile.addEventListener("click", goToEditProfile);
accountPrivateSet.addEventListener("click", goToEditAccountPrivate);
alterAccount.addEventListener("click", goToEditAccount);

function goToEditProfile(){
    window.location.href = "/edit/profile";
}

function goToEditAccount(){
    window.location.href = "/edit/account";
}

function goToEditAccountPrivate(){
    window.location.href = "/edit/accountPrivate";
}