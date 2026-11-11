let editDisplayName = document.querySelector("#editDisplayName");
let editAvatar = document.querySelector("#editAvatar");
document.addEventListener("DOMContentLoaded", ()=>{
    getEditProfileInfo();
});
const alterDisplayNameAssure = document.querySelector("#alterDisplayNameAssure");
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
let editBio = document.querySelector("#editBio");
let editBioRemaining = document.querySelector("#editBioRemaining");
const BiomaxLength = 200;
const bioEditBtn = document.querySelector("#bioEditBtn");
let alterDisplayNameInput = document.querySelector("#alterDisplayNameInput");
let alterDisplayNameSuccess = document.querySelector("#alterDisplayNameSuccess");

alterDisplayNameAssure.addEventListener("click", alterDisplayNameFunc);
bioEditBtn.addEventListener("click", alterBio);

editBio.addEventListener("input", bioContentRemainWords);
bioContentRemainWords();

function bioContentRemainWords(){
    const currentBioLength = editBio.value.length;
    editBioRemaining.innerText = `${currentBioLength} / ${BiomaxLength}`;
}

async function alterBio() {
    let formdata = new FormData();
    formdata.append("text", editBio.value);
    const response = await fetch("/api/edit/profile/bio",{
        method: "PATCH",
        body: formdata
    });
    const result = await response.json();
    if(result.ok){
        window.location.reload();
    }
}

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
    alterDisplayNameSuccess.style.display = "none";
    const response = await fetch("/api/getEditProfileInfo", {
        method: "GET"
    });
    const result = await response.json();
    editDisplayName.innerText = result.display_name;
    editAvatar.src = result.avatar_url;
    editBio.value = result.bio;
    alterDisplayNameInput.placeholder = `當前顯示名稱: ${result.display_name}`;
    const currentBioLength = editBio.value.length;
    editBioRemaining.innerText = `${currentBioLength} / ${BiomaxLength}`;
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


async function alterDisplayNameFunc() {
    let formdata = new FormData();
    formdata.append("display_name", alterDisplayNameInput.value);
    const response = await fetch("/api/edit/displayName", {
        method: "PATCH",
        body: formdata
    })
    const result = await response.json();
    if(result.ok){
        alterDisplayNameInput.placeholder = `當前顯示名稱: ${result.display_name}`;
        alterDisplayNameSuccess.style.display = "block";
    }
}
