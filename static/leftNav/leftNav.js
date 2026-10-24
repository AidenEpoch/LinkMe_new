const leftNavShow = document.querySelector("#leftNavShow");
const leftNavHidden = document.querySelector("#leftNavHidden");

const postBlock = document.querySelector("#postBlock");
const clubBlock = document.querySelector("#clubBlock");
const searchBlock = document.querySelector("#searchBlock");
const linkMeBlock = document.querySelector("#linkMeBlock");
const messageBlock = document.querySelector("#messageBlock");
const userBlock = document.querySelector("#userBlock");

const postDialog = document.querySelector("#postDialog");
const closePostWindow = document.querySelector("#closePostWindow");



const homePageIcon = document.querySelector("#homePageIcon");


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

function closePostDialogWindow(){
    postDialog.close();
}

async function goToMessage() {
    
}



async function goToLinkMe() {
    const response = await fetch("/api/auth", {
        method: "GET"
    })
    const result = await response.json();
    if(result.ok){
        window.location.href = "/linkme";
    }else{
        window.location.href = "/";
    }
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
    leftNavHidden.style.display = "flex";
    leftNavShow.style.display = "none";
}

function hideNav(){
    leftNavHidden.style.display = "none";
    leftNavShow.style.display = "flex";
}