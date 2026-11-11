document.addEventListener("DOMContentLoaded", ()=>{
    getLinkMeUserInfo();
    getFollowInfo();
})
let linkMeAvatar = document.querySelector("#linkMeAvatar");
let linkMeUserName = document.querySelector("#linkMeUserName");
let linkMeBio = document.querySelector("#linkMeBio");
let linkMeBtn = document.querySelector("#linkMeBtn");
let rejectBtn = document.querySelector("#rejectBtn");


const rejectPopUp = document.querySelector("#rejectPopUp");
const thinkTwice = document.querySelector("#thinkTwice");
const goodBye = document.querySelector("#goodBye");
let decideLink = document.querySelector("#decideLink");
const doubleOp = document.querySelector("#doubleOp");
let missSection = document.querySelector("#missSection");

async function getLinkMeUserInfo() {
    let keyword = window.location.pathname.split("/").filter(Boolean).pop();
    const response = await fetch(`/api/linkMeGetUser?userName=${encodeURIComponent(keyword)}`);
    const result = await response.json();
    if(result.ok){
        linkMeAvatar.src = result.avatar_url;
        linkMeUserName.innerText = result.display_name;
        if(result.bio != null){
            linkMeBio.innerText = `個人簡介${result.bio}`;
        }else{
            linkMeBio.innerText = "這位朋友沒有分享簡介內容";
        }
    }
}

linkMeBtn.addEventListener("click", 
    async function() {
        if(linkMeBtn.innerText == "已追蹤" || linkMeBtn.innerText == "已送出追蹤申請"){
            return;
        }
        const user_name = decodeURIComponent(window.location.pathname.slice(8));
        console.log(user_name);
        const response = await fetch(`/api/follow/${encodeURIComponent(user_name)}`, {
            method: "POST"
        })
        const result = await response.json();
         if(result.ok){
            if(result.wait_for_follow){
                linkMeBtn.innerText = "已送出追蹤申請";
            }else{
                linkMeBtn.innerText = "已追蹤";
                const followResponse = await fetch(`/api/follow/notification/${encodeURIComponent(user_name)}`, {
                    method: "POST"
                })
                const followResult = await followResponse.json();
                if(followResult.ok){
                    window.location.reload();
                }
            }
        }
    })

async function getFollowInfo() {
    const user_name = decodeURIComponent(window.location.pathname.slice(8));
    const response_skip = await fetch(`/api/linkme/isSkip/${encodeURIComponent(user_name)}`, {
        method: "GET"
    });
    let result_skip = await response_skip.json();
    if(result_skip.skip){
        linkMeBtn.style.display = "none";
        rejectBtn.style.display = "none";
        missSection.style.display = "block";
    }
    const response = await fetch(`/api/isfollow/${user_name}`, {
        method: "GET"
    });
    const result = await response.json();
    if(result.is_follow){
        linkMeBtn.innerText = "已追蹤";
    }else if(result.is_waiting){
        linkMeBtn.innerText = "已送出追蹤申請";
    }

}


rejectBtn.addEventListener("click", openRejectDialog);
thinkTwice.addEventListener("click", closeRejectDialog);
goodBye.addEventListener("click", missTheChance);

function openRejectDialog(){
    if(linkMeBtn.innerText == "已追蹤" || linkMeBtn.innerText == "已送出追蹤申請"){
        doubleOp.style.display = "block";
        return;
    }
    rejectPopUp.showModal();
    document.body.style.overflow = "hidden";
}

function closeRejectDialog(){
    rejectPopUp.close();
     document.body.style.overflow = "";
}

async function missTheChance(){
    const user_name = decodeURIComponent(window.location.pathname.slice(8));
    const response = await fetch(`/api/linkme/skip/${user_name}`, {
        method: "POST"
    });
    const result = await response.json();
    if(result.ok){
        missSection.style.display = "block";
        rejectPopUp.close();
        linkMeBtn.style.display = "none";
        rejectBtn.style.display = "none";
    }
}
