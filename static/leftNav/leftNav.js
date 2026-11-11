const leftNavShow = document.querySelector("#leftNavShow");
const leftNavHidden = document.querySelector("#leftNavHidden");

const postBlock = document.querySelector("#postBlock");
const clubBlock = document.querySelector("#clubBlock");
const searchBlock = document.querySelector("#searchBlock");
const linkMeBlock = document.querySelector("#linkMeBlock");
const messageBlock = document.querySelector("#messageBlock");
const userBlock = document.querySelector("#userBlock");
const logoutBlock = document.querySelector("#logoutBlock");

const postDialog = document.querySelector("#postDialog");
const closePostWindow = document.querySelector("#closePostWindow");

let isMessageOpen = false;

const homePageIcon = document.querySelector("#homePageIcon");

logoutBlock.addEventListener("mouseenter", logoutSelect);
logoutBlock.addEventListener("mouseleave", logoutLeave);
logoutBlock.addEventListener("click", logoutLinkMe);

leftNavShow.addEventListener("mouseenter", showHiddenNav);
leftNavHidden.addEventListener("mouseleave", hideNav);

homePageIcon.addEventListener("mouseenter", homeSelect);
homePageIcon.addEventListener("mouseleave", homeExit);
homePageIcon.addEventListener("click", goToHome);

postBlock.addEventListener("mouseenter", postSelect);
postBlock.addEventListener("mouseleave", postLeave);
postBlock.addEventListener("click", goToPost);

clubBlock.addEventListener("mouseenter", clubSelect);
clubBlock.addEventListener("mouseleave", clubLeave);
clubBlock.addEventListener("click", goToClub);

searchBlock.addEventListener("mouseenter", searchSelect);
searchBlock.addEventListener("mouseleave", searchLeave);
searchBlock.addEventListener("click", goToSearch);

linkMeBlock.addEventListener("mouseenter", linkMeSelect);
linkMeBlock.addEventListener("mouseleave", linkMeLeave);
linkMeBlock.addEventListener("click", goToLinkMe);

messageBlock.addEventListener("mouseenter", messageSelect);
messageBlock.addEventListener("mouseleave", messageLeave);
messageBlock.addEventListener("click", goToMessage);


userBlock.addEventListener("mouseenter", userSelect);
userBlock.addEventListener("mouseleave", userLeave);
userBlock.addEventListener("click", goToUser);


closePostWindow.addEventListener("click", closePostDialogWindow);

document.addEventListener("DOMContentLoaded", ()=>{
    getNotification();
    getLinkMeRemaining();
    getAvatarIcon();
});

const userAvatarIcon = document.querySelector("#userAvatar_icon");
const userAvatarIconHidden = document.querySelector("#userAvatar_iconHidden");

async function getAvatarIcon() {
    const response = await fetch("/api/user", {
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        let userNamePost = document.querySelector("#userNamePost");
        if(result.data.avatar_url){
            userAvatarIcon.src = result.data.avatar_url;
            userAvatarIconHidden.src = result.data.avatar_url;
            userNamePost.innerHTML = `
                <div class = "postUserPresent">
                    <img src = ${result.data.avatar_url} id = "userAvatar_postReady">
                    <div>${result.data.display_name}</div>
                </div>
            `
        }else{
            userAvatarIcon.src = "/static/image/avatar_default.png";
            userAvatarIconHidden = "/static/image/avatar_default.png";
            userNamePost.innerHTML = `
                <div class = "postUserPresent">
                    <img src = "/static/image/avatar_default.png" id = "userAvatar_postReady">
                    <div>${result.data.display_name}</div>
                </div>
            `
        }
    }
}

let reminderHidden = document.querySelector("#reminderHidden");
let notified_reminderIconHidden = document.querySelector("#notified_reminderIconHidden");
let reminderIcon = document.querySelector("#reminderIcon");
let notified_reminderIcon = document.querySelector("#notified_reminderIcon");

async function getNotification() {
    const response = await fetch("/api/notificationGet",{
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        if(result.hasNotification){
            notified_reminderIconHidden.style.display = "block";
            notified_reminderIcon.style.display = "block";
            reminderHidden.style.display = "none";
            reminderIcon.style.display = "none";

        }else{
            notified_reminderIconHidden.style.display = "none";
            notified_reminderIcon.style.display = "none";
            reminderHidden.style.display = "block";
            reminderIcon.style.display = "block";
        }
    }
}


async function logoutLinkMe(){
    const response = await fetch("/api/logout", {
        method: "POST"
    })
    const result = await response.json();
    if(result.ok){
        window.location.href = "/";
    }
}

function closePostDialogWindow(){
    postDialog.close();
    document.body.style.overflow = "";
}

async function goToMessage() {
    
}

function logoutSelect(){
    logoutBlock.style.backgroundColor = "rgb(177, 176, 176)";
    logoutBlock.style.borderRadius = "10px";
}

function logoutLeave(){
    logoutBlock.style.backgroundColor = "";
    logoutBlock.style.borderRadius = "";
}



async function goToSearch(){
    const response = await fetch("/api/auth", {
        method: "GET"
    })
    const result = await response.json();
    if(result.ok){
        window.location.href = "/search";
    }else{
        window.location.href = "/";
    }
}

async function goToUser() {
    const response = await fetch("/api/user",{
        method: "GET"
    })
    const result = await response.json();
    if(result.ok){
        const user_Name = result.data.user_name;
        const getUserName = await fetch(`/api/users/${user_Name}`,{
            method: "GET"
        });
        let userName = await getUserName.json();
        userName = userName.data.display_name;
        window.location.href = `/${user_Name}`;
    }else{
        window.location.href = "/";
    }
}

async function goToClub(){
    const response = await fetch("/api/auth",{
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        window.location.href = "/club";
    }else{
        window.location.href = "/";
    }
}

function goToPost(){
    postDialog.showModal();
    closePostWindow.style.display = "block";
    document.body.style.overflow = "hidden";
}

function goToHome(){
    window.location.href = "/";
}

function userSelect(){
    userBlock.style.backgroundColor = "rgb(177, 176, 176)";
    userBlock.style.borderRadius = "10px";
}

function userLeave(){
    userBlock.style.backgroundColor = "";
    userBlock.style.borderRadius = "";
}

function messageSelect(){
    messageBlock.style.backgroundColor = "rgb(177, 176, 176)";
    messageBlock.style.borderRadius = "10px";
}

function messageLeave(){
    messageBlock.style.backgroundColor = "";
    messageBlock.style.borderRadius = "";
}

function linkMeSelect(){
    linkMeBlock.style.backgroundColor = "rgb(177, 176, 176)";
    linkMeBlock.style.borderRadius = "10px";
}

function linkMeLeave(){
    linkMeBlock.style.backgroundColor = "";
    linkMeBlock.style.borderRadius = "";
}

function searchSelect(){
    searchBlock.style.backgroundColor = "rgb(177, 176, 176)";
    searchBlock.style.borderRadius = "10px";
}

function searchLeave(){
    searchBlock.style.backgroundColor = "";
    searchBlock.style.borderRadius = "";
}

function homeSelect(){
    homePageIcon.style.backgroundColor = "rgb(177, 176, 176)";
    homePageIcon.style.borderRadius = "10px";
}

function homeExit(){
    homePageIcon.style.backgroundColor = "";
    homePageIcon.style.borderRadius = "";
}

function postSelect(){
    postBlock.style.backgroundColor = "rgb(177, 176, 176)";
    postBlock.style.borderRadius = "10px";
}

function postLeave(){
    postBlock.style.backgroundColor = "";
    postBlock.style.borderRadius = "";
}

function clubSelect(){
    clubBlock.style.backgroundColor = "rgb(177, 176, 176)";
    clubBlock.style.borderRadius = "10px";
}

function clubLeave(){
    clubBlock.style.backgroundColor = "";
    clubBlock.style.borderRadius = "";
}


function showHiddenNav(){
    if(isMessageOpen){
        return;
    }
    leftNavHidden.style.display = "flex";
    leftNavShow.style.display = "none";
    logoutBlock.style.display = "grid";
}

function hideNav(){
    if(isMessageOpen){
        return;
    }
    leftNavHidden.style.display = "none";
    leftNavShow.style.display = "flex";
    logoutBlock.style.display = "none";
}




/*  #################################### 貼文 ########################################## */

const uploadBtn = document.querySelector("#uploadBtn");
const postDialogNext = document.querySelector("#postDialogNext");
const postPreview = document.querySelector("#postPreview");
const returnToFirst = document.querySelector("#returnToFirst");
const goToNextStepBtn = document.querySelector("#goToNextStep");
const postDialogLast = document.querySelector("#postDialogLast");
const postTheCreate = document.querySelector("#postTheCreate");
const returnToSecond = document.querySelector("#returnToSecond");
const closePostWindowLast = document.querySelector("#closePostWindowLast");

const closePostWindowNext = document.querySelector("#closePostWindowNext");

let previewURL = null;

uploadBtn.addEventListener("change", goToNextUpload);

returnToFirst.addEventListener("click", returnToFirstPostPage);

closePostWindowNext.addEventListener("click", closeNextWindow);

returnToSecond.addEventListener("click", returnToSecondStep);

closePostWindowLast.addEventListener("click", closeFinalWindow);

function closeFinalWindow(){
    postDialogLast.close();
    document.body.style.overflow = "";
}

function returnToSecondStep(){
    postDialogNext.showModal();
    postDialogLast.close();
    document.body.style.overflow = "hidden";
}

goToNextStepBtn.addEventListener("click", goToPostStep);

function goToPostStep(){
    const file = uploadBtn.files[0];
    if (!file){
        return;
    }else{
        console.log("file: ", file);
        if(!file.type.startsWith("image/")){
            alert("目前只支援圖片");
            return;
        }

        if(previewURL){
            URL.revokeObjectURL(previewURL);
        }
        let previewBeforePost = document.querySelector("#previewBeforePost");
        previewURL = URL.createObjectURL(file);
        previewBeforePost.style.backgroundImage = `url(${previewURL})`;
        previewBeforePost.style.backgroundSize = "cover";
        previewBeforePost.style.backgroundRepeat = "no-repeat";
        postDialogLast.showModal();
        postDialogNext.close();
        closePostWindowLast.style.display = "block";
    }
}

function returnToFirstPostPage(){
    postDialog.showModal();
    postDialogNext.close();
    closePostWindowNext.style.display = "none";
    closePostWindow.style.display = "block";
    document.body.style.overflow = "hidden";
}

function closeNextWindow(){
    postDialogNext.close();
    document.body.style.overflow = "";
}

function goToNextUpload(){
    const file = uploadBtn.files[0];
    if (!file){
        return;
    }else{
        console.log("file: ", file);
        if(!file.type.startsWith("image/")){
            alert("目前只支援圖片");
            return;
        }

        if(previewURL){
            URL.revokeObjectURL(previewURL);
        }
        previewURL = URL.createObjectURL(file);
        postPreview.style.backgroundImage = `url(${previewURL})`;
        postPreview.style.backgroundSize = "cover";
        postPreview.style.backgroundRepeat = "no-repeat";
        postDialog.close();
        postDialogNext.showModal();
        closePostWindowNext.style.display = "block";
    }
}

postTheCreate.addEventListener("click", postIt);

async function postIt() {
    const file = uploadBtn.files[0];
    const postContent = document.querySelector("#postContent")
    const text = postContent.value;
    let formdata = new FormData();
    formdata.append("file", file);
    formdata.append("text", text);
    const response = await fetch("/api/postUpload", {
        method: "Post",
        body: formdata,
    });
    const result = await response.json();
    let user_name = result.data;
    if(result.ok){
        window.location.href = `/${user_name}`;
    }
}

const postContent = document.querySelector("#postContent");
const remainingCount = document.querySelector("#remainingCount");

const maxLength = 2200;

postContent.addEventListener("input", remainingwords);

function remainingwords(){
    const currentLength = postContent.value.length;
    const remaining = maxLength - currentLength;

    remainingCount.textContent = `${currentLength} / ${maxLength}`;
}



/* LinkMe 頁面 */
let linkMeDialog = document.querySelector("#linkMeDialog");
let linkMeCloseDialog = document.querySelector("#linkMeCloseDialog");
let linkMeDialogBtn = document.querySelector("#linkMeDialogBtn");

linkMeCloseDialog.addEventListener("click", closeLinkMeSection);
linkMeDialogBtn.addEventListener("click", startLinkMe);

async function goToLinkMe() {
    const response = await fetch("/api/auth", {
        method: "GET"
    })
    const result = await response.json();
    if(result.ok){
        linkMeDialog.showModal();
        document.body.style.overflow = "hidden";
    }else{
        window.location.href = "/";
    }
}

function closeLinkMeSection(){
    linkMeDialog.close();
    document.body.style.overflow = "";
}

async function getLinkMeRemaining() {
    const response = await fetch("/api/match/remaining",{
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        linkMeDialogBtn.innerText = `LinkMe(${result.remaining} / 3)`
    }
}

async function startLinkMe() {
    const response = await fetch("/api/match/draw", {
        method: "POST"
    })
    const result = await response.json();
    if(result.ok){
        window.location.href = `/linkme/${result.matched_user.user_name}`;
    }
}