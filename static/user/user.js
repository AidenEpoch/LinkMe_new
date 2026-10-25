let avatar_name = document.querySelector("#avatar_name");
let readStore = document.querySelector("#readStoreBtn");
let editProfile = document.querySelector("#editProfileBtn");
let postShow = document.querySelector("#postShow");
const closePost = document.querySelector("#closePostShow");

closePost.addEventListener("click", closePostShow);

function closePostShow(){
    postShow.close();
}

addEventListener("DOMContentLoaded", ()=>{
    getUserInformation(); 
    getUserPosts();
    checkFollow();
});

async function showPost(post_id) {
    closePost.style.display = "block";
    const response = await fetch(`/api/showPost/${post_id}`, {
        method: "GET"
    })
    const result = await response.json();
    postShow.querySelectorAll(".postSect").forEach(element => {
        element.remove();
    });
    let postSection = document.createElement("div");
    let postImg = document.createElement("div");
    let postInfo = document.createElement("div");
    let postName = document.createElement("div");
    let postContent = document.createElement("p");
    let hr = document.createElement("hr");
    postName.className = "postName";
    postContent.className = "postContent";
    postInfo.className = "postInfo";
    postSection.className = "postSect";
    postImg.className = "postImg";
    postContent.innerText = result.content;
    postName.innerText = result.name;
    postImg.style.backgroundImage = `url(${result.img_url})`;
    postShow.appendChild(postSection);
    postSection.appendChild(postImg);
    postInfo.appendChild(postName);
    postInfo.appendChild(postContent);
    postSection.appendChild(postInfo);
    postShow.showModal();
}

async function getUserInformation(){
    const user_name = decodeURIComponent(window.location.pathname.slice(1));
    const response = await fetch(`/api/users/${encodeURIComponent(user_name)}`, {
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        const display_name = result.data.display_name;
        avatar_name.innerHTML = display_name;   
        if(result.data.is_owner){
            readStore.style.display = "flex";
            editProfile.style.display = "flex";
            followBtn.style.display = "none";

        }else{
            readStore.style.display = "none";
            editProfile.style.display = "none";
            followBtn.style.display = "flex";
        }
    }
}

async function getUserPosts() {
    const user_name = decodeURIComponent(window.location.pathname.slice(1));
    const response = await fetch(`/api/GetPost/${encodeURIComponent(user_name)}`, {
        method: "GET"
    });
    const result = await response.json();
    let postContainer = document.querySelector("#userPostGrid");
    if(result.ok){
        let posts = result.data;
        if (!Array.isArray(posts) || posts.length === 0) {
            postContainer.textContent = "尚無貼文";
            return;
        }

        posts.forEach(post => {
            let postItem = document.createElement("div");
            postItem.className = "userPostItem";

            const image = document.createElement("img");
            image.src = post.image_url;
            image.alt = post.content || "貼文";
            image.loading = "lazy";

            postItem.appendChild(image);
            postContainer.append(postItem);

            postItem.addEventListener("click", () => {
                showPost(post.id);
            })
        });
    }
}



/* ######################## 追蹤 ############################ */
let followBtn = document.querySelector("#followBtn");
let followWord = document.querySelector("#followWord");
followBtn.addEventListener("click", followOthers);

async function followOthers(){
    const user_name = decodeURIComponent(window.location.pathname.slice(1));
    if(followWord.innerText == "追蹤"){
        const response = await fetch(`/api/follow/${encodeURIComponent(user_name)}`, {
            method: "POST"
        })
        const result = await response.json();
        if(result.ok){
            followWord.innerText = "已追蹤";
        }
    }else if(followWord.innerHTML == "已追蹤"){
        const response = await fetch(`/api/deleteFollow/${encodeURIComponent(user_name)}`, {
            method: "DELETE"
        })
        const result = await response.json();
        if(result.ok){
            followWord.innerText = "追蹤";
        }
    }
}


async function checkFollow() {
    const user_name = decodeURIComponent(window.location.pathname.slice(1));
    const response = await fetch(`/api/isfollow/${encodeURIComponent(user_name)}`, {
        method: "GET"
    })
    const result = await response.json();
    if(result.is_follow){
        followWord.innerText = "已追蹤";
    }else if(result.not_follow){
        followWord.innerText = "追蹤";
    }
}

/*########################################################## */

