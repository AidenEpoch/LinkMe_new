/* ###############################以下是左導覽列的 Icon 部分 ############################## */
const userPage = document.querySelector("#userPage");
const alarmPage = document.querySelector("#alarmPage");
const clubPage = document.querySelector("#clubPage");
const linkPage = document.querySelector("#linkPage");
const searchPage = document.querySelector("#searchPage");
const postPage = document.querySelector("#postPage");
const goToHome = document.querySelector("#goToHome");
const navBanner = document.querySelectorAll(".navBanner");
const leftNav = document.querySelector(".leftNav");
const navBlock = document.querySelectorAll(".navBlock");


const userPageShow = document.querySelector("#userPageShow");
const alarmPageShow = document.querySelector("#alarmPageShow");
const clubPageShow = document.querySelector("#clubPageShow");
const linkPageShow = document.querySelector("#linkPageShow");
const searchPageShow = document.querySelector("#searchPageShow");
const postPageShow = document.querySelector("#postPageShow");
const goToHomeShow = document.querySelector("#goToHomeShow");



/* ###################################################################################### */


/* 以下是左導覽列的 Block 部分 */
const userPageBlock = document.querySelector("#userPageBlock");
const alarmPageBlock = document.querySelector("#alarmPageBlock");
const clubPageBlock = document.querySelector("#clubPageBlock");
const searchPageBlock = document.querySelector("#searchPageBlock");
const postPageBlock = document.querySelector("#postPageBlock");
const linkPageBlock = document.querySelector("#linkPageBlock");

/* ######################################################################################### */



userPageBlock.addEventListener("click", goToUserPage);
clubPageBlock.addEventListener("click", goToClubPage);
linkPageBlock.addEventListener("click", goToLinkMePage);
searchPageBlock.addEventListener("click", goToSearchPage);
goToHome.addEventListener("click", goToHomePage);


userPageShow.addEventListener("mouseenter", userPageSelect);
clubPageShow.addEventListener("mouseenter", clubPageSelect);
alarmPageShow.addEventListener("mouseenter", alarmPageSelect);
linkPageShow.addEventListener("mouseenter", linkMePageSelect);
postPageShow.addEventListener("mouseenter", postPageSelect);



userPageBlock.addEventListener("mouseleave", userPageLeave);
clubPageBlock.addEventListener("mouseleave", clubPageLeave);
alarmPageBlock.addEventListener("mouseleave", alarmPageLeave);
linkPageBlock.addEventListener("mouseleave", linkMePageLeave);
postPageBlock.addEventListener("mouseleave", postPageLeave);


leftNav.addEventListener("mouseleave", leftNavLeave);


function userPageSelect(){
    userPageBlock.style.backgroundColor = "rgb(177, 176, 176)";
    userPageBlock.style.borderRadius = "10px";
    navBanner.forEach((banner)=>{
        banner.style.visibility = "visible";
    })
}

function userPageLeave(){
    userPageBlock.style.backgroundColor = "";
}


function clubPageSelect(){
    clubPageBlock.style.backgroundColor = "rgb(177, 176, 176)";
    clubPageBlock.style.borderRadius = "10px";
    navBanner.forEach((banner)=>{
        banner.style.visibility = "visible";
    })
}

function clubPageLeave(){
    clubPageBlock.style.backgroundColor = "";
}

function alarmPageSelect(){
    alarmPageBlock.style.backgroundColor = "rgb(177, 176, 176)";
    alarmPageBlock.style.borderRadius = "10px";
    navBanner.forEach((banner)=>{
        banner.style.visibility = "visible";
    })
}

function alarmPageLeave(){
    alarmPageBlock.style.backgroundColor = "";
}

function linkMePageSelect(){
    linkPageBlock.style.backgroundColor = "rgb(177, 176, 176)";
    linkPageBlock.style.borderRadius = "10px";
    navBanner.forEach((banner)=>{
        banner.style.visibility = "visible";
    })
}

function linkMePageLeave(){
    linkPageBlock.style.backgroundColor = "";
}


function postPageSelect(){
    postPageBlock.style.backgroundColor = "rgb(177, 176, 176)";
    postPageBlock.style.borderRadius = "10px";
    navBanner.forEach((banner)=>{
        banner.style.visibility = "visible";
    })
}

function postPageLeave(){
    postPageBlock.style.backgroundColor = "";
}



function leftNavLeave(){
    navBanner.forEach((banner)=>{
        banner.style.visibility = "hidden";
    });
    navBlock.forEach((block) =>{
        block.style.backgroundColor = "";
    });
}

async function goToUserPage(){
    const response = await fetch("/api/auth", {
        method: "GET"
    });
    const result = await response.json();
    if (result.ok){
        window.location.href = "/user";
        console.log("成功點擊");
    }else{
        window.location.href = "/";
    }
}

async function goToClubPage(){
    const response = await fetch("/api/auth", {
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        window.location.href = "/club";
    }else{
        window.location.href = "/";
    }
}


async function goToLinkMePage(){
    const response = await fetch("/api/auth", {
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        window.location.href = "/linkme";
    }else{
        window.location.href = "/";
    }
}

async function goToSearchPage() {
    const response = await fetch("/api/auth", {
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        window.location.href = "/search";
    }else{
        window.location.href = "/";
    }
}

async function goToHomePage() {
    window.location.href = "/";
}



/*  ############################ 以下是彈出式視窗 #################################### */



/* ################################################################################### */