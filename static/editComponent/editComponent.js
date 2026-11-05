let editDisplayName = document.querySelector("#editDisplayName");
let editAvatar = document.querySelector("#editAvatar");
document.addEventListener("DOMContentLoaded", getEditProfileInfo);
const changeAvatar = document.querySelector("#changeAvatar");
const changeAvatarBtn = document.querySelector("#changeAvatarBtn");
changeAvatar.addEventListener("click", pressChangeAvatarBtn);
const uploadAvatar = document.querySelector("#uploadAvatar");
const setAvatar = document.querySelector("#setAvatar");
const closeAvatarSection = document.querySelector("#closeAvatarSet");
closeAvatarSection.addEventListener("click", closeAvatarSectBlock);
const avatarFileInput = document.querySelector("#avatarFileInput");
uploadAvatar.addEventListener("click", startUploadAvatar);
const removeAvatar = document.querySelector("#removeAvatar");
removeAvatar.addEventListener("click", removeChosenAvatar);

async function removeChosenAvatar(){
    editAvatar.src = "/static/image/avatar_default.png";
    setAvatar.close();
    document.body.style.overflow = "";

}

function startUploadAvatar(){
    avatarFileInput.click();
}

avatarFileInput.addEventListener("change", changeProfileAvatar);

function closeAvatarSectBlock(){
    setAvatar.close();
    document.body.style.overflow = "";
}


function pressChangeAvatarBtn(){
    setAvatar.showModal();
    document.body.style.overflow = "hidden";
}



async function getEditProfileInfo() {
    const response = await fetch("/api/getEditProfileInfo", {
        method: "GET"
    });
    const result = await response.json();
    editDisplayName.innerText = result.display_name;
    editAvatar.src = result.avatar_url;
}

async function changeProfileAvatar(){
    const file = avatarFileInput.files[0];
    if(!file){
        return;
    }
    const formdata = new FormData();
    formdata.append("file", file);

    const response = await fetch("/api/avatar/upload",{
        method: "POST",
        body: formdata
    });
    const result = await response.json();
    if(result.ok){
        if(result.avatar_url){
            editAvatar.src = result.avatar_url;
            alert("上傳成功");
            setAvatar.close();
            document.body.style.overflow = "";
            
        }else{
            editAvatar.src = "/static/image/avatar_default.png";
            alert("上傳時發生錯誤");
            setAvatar.close();
            document.body.style.overflow = "";
        }
    }
}

