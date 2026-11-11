const privateAccount = document.querySelector("#privateAccount");
privateAccount.addEventListener("change", setPrivacyOfAccount);
let privateStatus = document.querySelector("#privateStatus");
let publicStatus = document.querySelector("#publicStatus");
document.addEventListener("DOMContentLoaded", privateOrPublic);
async function setPrivacyOfAccount() {
    const newPrivacy = privateAccount.checked;
    let formdata = new FormData();
    formdata.append("privacy", privateAccount.checked);
    const response = await fetch("/api/edit/account/setPrivacy", {
        method: "PATCH",
        body: formdata
    })
    const result = await response.json();
    if(result.ok){
        privateStatus.style.display = newPrivacy ? "block" : "none";
        publicStatus.style.display = newPrivacy ? "none" : "block";
    }
}

async function privateOrPublic() {
    const response = await fetch("/api/edit/account/privacy", {
        method: "GET"
    })
    const result = await response.json();
    if(result.ok){
        privateAccount.checked = Boolean(result.is_private);
        console.log("is_private: ", result.is_private);
        if(result.is_private){
            privateStatus.style.display = "block";
            publicStatus.style.display = "none";
        }else{
            privateStatus.style.display = "none";
            publicStatus.style.display = "block";
        }
    }
}