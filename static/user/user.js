let avatar_name = document.querySelector("#avatar_name");
let readStore = document.querySelector("#readStoreBtn");
let editProfile = document.querySelector("#editProfileBtn");
let postShow = document.querySelector("#postShow");
const avatar_img = document.querySelector("#avatar_img");
const closePost = document.querySelector("#closePostShow");
const setAvatar = document.querySelector("#setAvatar");
const closeAvatarSet = document.querySelector("#closeAvatarSet");
const uploadAvatar = document.querySelector("#uploadAvatar");
const avatarFileInput = document.querySelector("#avatarFileInput");

closeAvatarSet.addEventListener("click", closeAvatarSect);
closePost.addEventListener("click", closePostShow);

function closeAvatarSect(){
    setAvatar.close();
    document.body.style.overflow = "";
}

function setAvatarImage(){
    setAvatar.showModal();
    document.body.style.overflow = "hidden";
}

function closePostShow(){
    postShow.close();
    document.body.style.overflow = "";
}

document.addEventListener("DOMContentLoaded", ()=>{
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
    postImg.style.backgroundSize = "cover";
    postImg.style.backgroundRepeat = "no-repeat";
    postShow.appendChild(postSection);
    postSection.appendChild(postImg);
    postInfo.appendChild(postName);
    postInfo.appendChild(postContent);
    postSection.appendChild(postInfo);
    postShow.showModal();
    document.body.style.overflow = "hidden";
}

let postNumber = document.querySelector("#postNumber");
let followerNumber = document.querySelector("#followerNumber");
let followingNumber = document.querySelector("#followingNumber");

async function getUserInformation(){
    const user_name = decodeURIComponent(window.location.pathname.slice(1));
    const response = await fetch(`/api/users/${encodeURIComponent(user_name)}`, {
        method: "GET"
    });
    const result = await response.json();
    if(result.no_user){
        window.location.href = "/";
    }
    if(result.ok){
        const display_name = result.data.display_name;
        avatar_name.innerHTML = display_name;  
        postNumber.innerHTML = `${result.data.postNumber} ` ;
        followerNumber.innerHTML = `${result.data.followerNumber}` ;
        followingNumber.innerHTML = `${result.data.followingNumber}`;
        if(result.data.is_owner){
            readStore.style.display = "flex";
            editProfile.style.display = "flex";
            followBtn.style.display = "none";
            uploadAvatar.addEventListener("click", changeAvatar);
            avatar_img.addEventListener("click", setAvatarImage);

        }else{
            readStore.style.display = "none";
            editProfile.style.display = "none";
            followBtn.style.display = "flex";
        }
        const avatar_url = result.data.avatar_url;

        avatar_img.style.backgroundImage = avatar_url
            ? `url("${avatar_url}")`
            : 'url("/static/image/avatar_default.png")';

        avatar_img.style.backgroundPosition = "center";
        avatar_img.style.backgroundSize = "cover";
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
        if(result.no_user){
            window.location.href = "/";
        }
        if(result.ok){
            followWord.innerText = "已追蹤";
            const followResponse = await fetch(`/api/follow/notification/${encodeURIComponent(user_name)}`, {
                method: "POST"
            })
            const followResult = await followResponse.json();
            if(followResult.ok){
                return;
            }
        }
        location.reload();
    }else if(followWord.innerHTML == "已追蹤"){
        const response = await fetch(`/api/deleteFollow/${encodeURIComponent(user_name)}`, {
            method: "DELETE"
        })
        const result = await response.json();
        if(result.ok){
            followWord.innerText = "追蹤";
        }
        location.reload();
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

/* ####################################   編輯  ############################## */

editProfile.addEventListener("click", openEditPage);

async function openEditPage() {
    window.location.href = "/edit";
}


/* ############################################################################ */

/* ###################################### 上傳大頭貼照 ################################# */
avatarFileInput.addEventListener("change", changeAvatarStart);

function changeAvatar() {
    avatarFileInput.click();
}

async function changeAvatarStart() {
    const file = avatarFileInput.files[0];
    if(!file){
        return;
    }else{
        console.log("file: ", file);
        let formdata = new FormData();
        formdata.append("file", file);
        const response = await fetch("/api/avatar/upload",{
            method:"POST",
            body: formdata
        });
        const result = await response.json();
        if(result.ok){
            avatar_img.style.backgroundImage = `url("${result.avatar_url}")`;
            setAvatar.close();
            document.body.overflow = "";
            alert("大頭貼更新成功");
        }else{
            alert("大頭貼上傳失敗");
        }
    }
}



/* #################################################################################### */


