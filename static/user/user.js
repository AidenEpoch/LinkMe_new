let avatar_name = document.querySelector("#avatar_name");
let readStore = document.querySelector("#readStoreBtn");
let editProfile = document.querySelector("#editProfileBtn");
const messageBtn = document.querySelector("#messageBtn");
let chatTargetUserId = null;
let postShow = document.querySelector("#postShow");
const avatar_img = document.querySelector("#avatar_img");
const closePost = document.querySelector("#closePostShow");
const setAvatar = document.querySelector("#setAvatar");
const closeAvatarSet = document.querySelector("#closeAvatarSet");
const uploadAvatar = document.querySelector("#uploadAvatar");
const avatarFileInput = document.querySelector("#avatarFileInput");
let userBioPresent = document.querySelector("#userBioPresent");
const removeAvatar = document.querySelector("#removeAvatar");
removeAvatar.addEventListener("click", removeAvatarFunction);

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
    try {
        const response = await fetch(`/api/showPost/${post_id}`);
        const result = await response.json();

        if (!response.ok || !result.ok) {
            throw new Error(result.message || "貼文載入失敗");
        }

        postShow.querySelectorAll(".postSect").forEach(element => {
            element.remove();
        });

        const postSection = document.createElement("div");
        postSection.className = "postSect";

        const postImg = document.createElement("div");
        postImg.className = "postImg";
        postImg.style.backgroundImage = `url("${result.img_url}")`;
        postImg.style.backgroundSize = "cover";
        postImg.style.backgroundPosition = "center";

        const postInfo = document.createElement("div");
        postInfo.className = "postInfo";

        const postName = document.createElement("div");
        postName.className = "postName";
        postName.textContent = result.name;

        const postContent = document.createElement("p");
        postContent.className = "postContent";
        postContent.textContent = result.content;

        const likeAndComment = document.createElement("div");
        likeAndComment.className = "postLikeAndComment";

        const postLike = document.createElement("img");
        postLike.className = "postLike";
        postLike.src = "/static/image/postLike.png";

        const postLikeHit = document.createElement("img");
        postLikeHit.className = "postLikeHit";
        postLikeHit.src = "/static/image/postLikeRed.png";

        const postComment = document.createElement("img");
        postComment.className = "postComment";
        postComment.src = "/static/image/postComment.png";

        let isLiked = Boolean(result.isLike ?? result.is_liked);

        function updateLike() {
            postLike.style.display = isLiked ? "none" : "block";
            postLikeHit.style.display = isLiked ? "block" : "none";
        }

        updateLike();

        let likeLoading = false;

        async function changeLike() {
            if (likeLoading) return;
            likeLoading = true;

            const formdata = new FormData();
            formdata.append("post_id", post_id);

            try {
                const url = isLiked
                    ? "/api/post/likeDelete"
                    : "/api/post/like";

                const response = await fetch(url, {
                    method: "PATCH",
                    body: formdata
                });

                const result = await response.json();

                if (!response.ok || !result.ok) {
                    throw new Error(result.message || "按讚操作失敗");
                }

                isLiked = !isLiked;
                updateLike();

            } catch (error) {
                alert(error.message);
            } finally {
                likeLoading = false;
            }
        }

        postLike.addEventListener("click", changeLike);
        postLikeHit.addEventListener("click", changeLike);

        likeAndComment.append(
            postLike,
            postLikeHit,
            postComment
        );

        // 直接使用與 search.js 相同的留言函式
        const commentSection = await createCommentSection(post_id);
        commentSection.style.display = "none";

        postComment.addEventListener("click", function() {
            const hidden = commentSection.style.display === "none";
            commentSection.style.display = hidden ? "flex" : "none";
        });

        postInfo.append(
            postName,
            postContent,
            likeAndComment,
            commentSection
        );

        postSection.append(postImg, postInfo);
        postShow.appendChild(postSection);

        closePost.style.display = "block";
        postShow.showModal();
        document.body.style.overflow = "hidden";

    } catch (error) {
        console.error("開啟貼文失敗:", error);
        alert(error.message);
    }
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
    console.log("個人頁面使用者資料：", result);
    if(result.no_user){
        window.location.href = "/";
    }
    if(result.ok){
        chatTargetUserId = Number(result.data.id);
        const display_name = result.data.display_name;
        avatar_name.innerHTML = display_name;  
        postNumber.innerHTML = `${result.data.postNumber} ` ;
        followerNumber.innerHTML = `${result.data.followerNumber}` ;
        followingNumber.innerHTML = `${result.data.followingNumber}`;
        if(result.data.is_owner){
            messageBtn.style.display = "none";
            readStore.style.display = "flex";
            editProfile.style.display = "flex";
            followBtn.style.display = "none";
            uploadAvatar.addEventListener("click", changeAvatar);
            avatar_img.addEventListener("click", setAvatarImage);

        }else{
            messageBtn.style.display = "flex";
            readStore.style.display = "none";
            editProfile.style.display = "none";
            followBtn.style.display = "flex";
        }
        const avatar_url = result.data.avatar_url;
        userBioPresent.innerText = result.data.bio;
        if(avatar_url){
            avatar_img.style.backgroundImage = avatar_url
            ? `url("${avatar_url}")`
            : 'url("/static/image/avatar_default.png")';

            avatar_img.style.backgroundPosition = "center";
            avatar_img.style.backgroundSize = "cover";
        }else{
            avatar_img.style.backgroundImage = "url('/static/image/avatar_default.png')";
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
        if(result.canView){
            let posts = result.data;
            if (!Array.isArray(posts) || posts.length === 0) {
                let postContainerTemp = document.createElement("div");
                postContainerTemp.className = "postContainerTemp";
                let postContainerTempWord = document.createElement("div");
                postContainerTempWord.textContent = "尚無貼文";
                postContainerTemp.appendChild(postContainerTempWord);
                postContainer.appendChild(postContainerTemp);
                return;
            }
            posts.forEach(post => {
            /*let postItem = document.createElement("div");
            postItem.className = "userPostItem";

            const image = document.createElement("img");
            image.src = post.image_url;
            image.alt = post.content || "貼文";
            image.loading = "lazy";

            postItem.appendChild(image);
            postContainer.append(postItem);*/
            let postItem = document.createElement("div");
            postItem.className = "userPostItem";
            postItem.innerHTML = `
                <img src = ${post.image_url} alt = "貼文" loading = "lazy">

            `
            postContainer.append(postItem);
            postItem.addEventListener("click", () => {
                showPost(post.id);
            })
        });
        }else{
            postContainer.textContent = "此用戶為私人帳戶，追蹤後可查看用戶貼文";
            return;
        }

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
            if(result.wait_for_follow){
                followWord.innerText = "已送出追蹤申請";
            }else{
                followWord.innerText = "已追蹤";
                const followResponse = await fetch(`/api/follow/notification/${encodeURIComponent(user_name)}`, {
                    method: "POST"
                })
                const followResult = await followResponse.json();
                if(followResult.ok){
                    window.location.reload();
                }
            }
        }
    }else if(followWord.innerText == "已追蹤"){
        const response = await fetch(`/api/deleteFollow/${encodeURIComponent(user_name)}`, {
            method: "DELETE"
        })
        const result = await response.json();
        if(result.ok){
            followWord.innerText = "追蹤";
        }
        location.reload();
    }else if(followWord.innerText == "已送出追蹤申請"){
        const response = await fetch(`/api/private/cancel/${encodeURIComponent(user_name)}`, {
            method: "PATCH"
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
        if(result.is_waiting){
            followWord.innerText = "已送出追蹤申請";
        }else{
            followWord.innerText = "追蹤";
        }
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
            window.location.reload();
        }else{
            alert("大頭貼上傳失敗");
        }
    }
}


async function removeAvatarFunction() {
    const response = await fetch("/api/avatar/remove", {
        method: "PATCH"
    });
    const result = await response.json();
    if(result.ok){
        window.location.reload();
    }
}


/* #################################################################################### */



messageBtn.addEventListener("click", startChat);

async function startChat() {
    if (!Number.isSafeInteger(chatTargetUserId) || chatTargetUserId <= 0) {
        alert("無法取得聊天對象的 ID");
        return;
    }

    messageBtn.style.pointerEvents = "none";

    try {
        const formData = new FormData();
        formData.append("other_user_id", chatTargetUserId);

        const response = await fetch("/api/chat/conversations", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok || !result.ok) {
            throw new Error(result.message || "建立聊天對話失敗");
        }

        console.log("聊天對話建立成功：", result);

        const conversationId = result.conversation_id;

        if (!conversationId) {
            throw new Error("API 沒有回傳 conversation_id");
        }

    // 開啟聊天室並自動選取剛剛建立的對話
    await window.openChatConversation(conversationId);


        } catch (error) {
            console.error("建立聊天對話失敗：", error);
            alert("無法建立聊天對話，請稍後再試");
        } finally {
            messageBtn.style.pointerEvents = "";
        }
    }


async function createCommentSection(postId) {
    const section = document.createElement("div");
    section.className = "postComments";

    const count = document.createElement("div");
    count.className = "postCommentCount";

    const list = document.createElement("div");
    list.className = "postCommentList";

    const form = document.createElement("form");
    form.className = "postCommentForm";

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "新增留言...";
    input.maxLength = 1000;
    input.required = true;

    const submit = document.createElement("button");
    submit.type = "submit";
    submit.textContent = "發布";

    form.append(input, submit);
    section.append(count, list, form);

    async function loadComments() {
        const response = await fetch(
            `/api/post/comments/${postId}`
        );

        const result = await response.json();

        if (!response.ok || !result.ok) {
            throw new Error(result.message || "載入留言失敗");
        }

        count.textContent = `留言 ${result.total} 則`;
        list.replaceChildren();

        result.comments.forEach(comment => {
            const item = document.createElement("div");
            item.className = "postCommentItem";

            const name = document.createElement("strong");
            name.textContent = comment.display_name;

            const content = document.createElement("p");
            content.textContent = comment.content;

            item.append(name, content);

            if (comment.is_owner) {
                const deleteBtn = document.createElement("button");
                deleteBtn.type = "button";
                deleteBtn.textContent = "刪除";

                deleteBtn.addEventListener("click", async () => {
                    deleteBtn.disabled = true;

                    try {
                        const response = await fetch(
                            `/api/post/comments/${comment.id}`,
                            { method: "DELETE" }
                        );

                        const result = await response.json();

                        if (!response.ok || !result.ok) {
                            throw new Error(result.message || "刪除留言失敗");
                        }

                        await loadComments();

                    } catch (error) {
                        alert(error.message);
                    } finally {
                        deleteBtn.disabled = false;
                    }
                });

                item.appendChild(deleteBtn);
            }

            list.appendChild(item);
        });
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const content = input.value.trim();
        if (!content) return;

        const data = new FormData();
        data.append("post_id", postId);
        data.append("content", content);

        submit.disabled = true;

        try {
            const response = await fetch(
                "/api/post/comments",
                {
                    method: "POST",
                    body: data
                }
            );

            const result = await response.json();

            if (!response.ok || !result.ok) {
                throw new Error(result.message || "發布留言失敗");
            }

            input.value = "";
            await loadComments();

        } catch (error) {
            alert(error.message);
        } finally {
            submit.disabled = false;
        }
    });

    try {
        await loadComments();
    } catch (error) {
        count.textContent = "留言載入失敗";
        console.error("載入留言失敗:", error);
    }

    return section;
}

