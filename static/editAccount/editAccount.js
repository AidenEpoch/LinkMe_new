const alterPassWord = document.querySelector("#alterPassWord");
const alterEmail = document.querySelector("#alterEmail");
let passwordNotTheSame = document.querySelector("#passwordNotTheSame");
let oldPasswordWrong = document.querySelector("#oldPasswordWrong");
let passwordEditSuccess = document.querySelector("#passwordEditSuccess");
let editEmailSuccess = document.querySelector("#editEmailSuccess");
const newEmail = document.querySelector("#newEmail");

alterPassWord.addEventListener("click", openAlterPasswordDialog);
alterEmail.addEventListener("click", openAlterEmailDialog);

function openAlterEmailDialog(){
    let alterEmailDialog = document.querySelector("#alterEmailDialog");
    alterEmailDialog.showModal();
}



function openAlterPasswordDialog(){
    let alterPassWordDialog = document.querySelector("#alterPassWordDialog");
    alterPassWordDialog.showModal();
}

const closeAlterPassword = document.querySelector("#closeAlterPassword");
closeAlterPassword.addEventListener("click", closeAlterPasswordDialog);

function closeAlterPasswordDialog(){
    let alterPassWordDialog = document.querySelector("#alterPassWordDialog");
    newPassword.value = "";
    newPasswordAssure.value = "";
    oldPassword.value = "";
    passwordNotTheSame.style.display = "none";
    oldPasswordWrong.style.display = "none";
    passwordEditSuccess.style.display = "none";
    alterPassWordDialog.close();
}

const closeAlterEmail = document.querySelector("#closeAlterEmail");
closeAlterEmail.addEventListener("click", closeAlterEmailDialog);

function closeAlterEmailDialog(){
    let alterEmailDialog = document.querySelector("#alterEmailDialog");
    editEmailSuccess.style.display = "none";
    newEmail.value = "";
    alterEmailDialog.close();
}

const editPasswordBtn = document.querySelector("#editPasswordBtn");
const editEmailBtn = document.querySelector("#editEmailBtn");

editPasswordBtn.addEventListener("click", changePassword);
editEmailBtn.addEventListener("click", changeEmail);

/* #################################### 修改密碼 ############################################################ */
const oldPassword = document.querySelector("#oldPassword");
let alterPassWordDialog = document.querySelector("#alterPassWordDialog");

async function changePassword() {
    const newPassword = document.querySelector("#newPassword");
    const newPasswordAssure = document.querySelector("#newPasswordAssure");
    let formdata = new FormData();
    formdata.append("newPassword", newPassword.value);
    formdata.append("oldPassword", oldPassword.value);
    const response_checked = await fetch("/api/edit/account/password_check", {
        method: "POST",
        body: formdata
    });
    const result_check = await response_checked.json();
    if(result_check.ok){
            if(newPassword.value === newPasswordAssure.value){
                const response = await fetch("/api/edit/account/password",{
                    method:"PATCH",
                    body: formdata
                });
                const result = await response.json();
                if(result.ok){
                    passwordEditSuccess.style.display = "block";
                    passwordNotTheSame.style.display = "none";
                    oldPasswordWrong.style.display = "none";
                }
            }else{
                passwordNotTheSame.style.display = "block";
                oldPasswordWrong.style.display = "none";
                passwordEditSuccess.style.display = "none";
            }
    }else{
        oldPasswordWrong.style.display = "block";
        passwordNotTheSame.style.display = "none";
        passwordEditSuccess.style.display = "none";
    }
}

async function changeEmail() {
    let formdata = new FormData();
    formdata.append("email", newEmail.value.trim());
    const response = await fetch("/api/edit/account/email", {
        method: "PATCH",
        body: formdata
    })
    const result = await response.json();
    if(result.ok){
        editEmailSuccess.style.display = "block";
    }
}

