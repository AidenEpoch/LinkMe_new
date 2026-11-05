document.addEventListener("DOMContentLoaded", getLinkMeUserInfo)
let linkMeAvatar = document.querySelector("#linkMeAvatar");
let linkMeUserName = document.querySelector("#linkMeUserName");
let linkMeBio = document.querySelector("#linkMeBio");

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