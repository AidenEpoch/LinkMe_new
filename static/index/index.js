const avatar_name = document.querySelector("#user_name"); 
let postContainer = document.querySelector("#postContainer");
const sentinel = document.querySelector("#sentinel");
const LinkMeRecordContainer = document.querySelector("#LinkMeRecordContainer");
const userAvatar = document.querySelector("#userAvatar");

const options = {
    root: null,
    rootMargin: "300px 0px",
    threshold: 0
}
let observer = new IntersectionObserver(observeCallBack, options);


document.addEventListener("DOMContentLoaded", () => {
    getUserInformation();
    observer.observe(sentinel);
    getFriendStatus();
    loadMatched();
})

async function loadMatched() {
    const response = await fetch("/api/linkme/getAllUser", {
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        result.matchedMember.forEach(matched_member =>{
            let matchedBlock = document.createElement("div");
            matchedBlock.className = "LinkMeRecordBlock";
            matchedBlock.innerHTML = `
                <img src="${matched_member.avatar_url}" class = "matchedMemberAvatar">
                <div class = "matchedMemberDisplayName">${matched_member.display_name}</div>
            `
            LinkMeRecordContainer.appendChild(matchedBlock);
            matchedBlock.addEventListener("click", function(){
                window.location.href = `/linkme/${matched_member.user_name}`;
            })
        })
    }

}


let hasMore = true;
let isLoading = false;
let nextCursor = null;

async function getFollowingPost(){

    if((hasMore == false) || (isLoading == true)){
        return;
    }
    isLoading = true;
    try{
        let url = "/api/indexPost";
        if(nextCursor != null){
            const params = new URLSearchParams(nextCursor);
            url += `?${params.toString()}`;
        }
        const response = await fetch(url, {
            method: "GET"
        })

        const result = await response.json();
        if(result.no_follow){
        }
        else if(result.ok){
            let posts = result.posts;
            posts.forEach(post => {
                let postSect = document.createElement("div");
                postSect.className = "postSect";
                let postBanner = document.createElement("div");
                postBanner.className = "postBanner";
                let post_avatar = document.createElement("img");
                post_avatar.className = "post_avatar";
                post_avatar.src = post.avatar_url || "/static/image/avatar_default.png";
                let indexPostUserNamePresent = document.createElement("div");
                indexPostUserNamePresent.className = "indexPostUserNamePresent";
                indexPostUserNamePresent.innerText = post.display_name;
                postBanner.appendChild(post_avatar);
                postBanner.appendChild(indexPostUserNamePresent);
                let indexPostImage = document.createElement("img");
                indexPostImage.className = "indexPostImage";
                indexPostImage.src = post.image_url;
                let indexPostLikeAndComment = document.createElement("div");
                indexPostLikeAndComment.className = "indexPostLikeAndComment";

                let indexPostLike = document.createElement("img");
                indexPostLike.className = "indexPostLike";
                indexPostLike.src = "/static/image/postLike.png";

                let indexPostLikeHit = document.createElement("img");
                indexPostLikeHit.className = "indexPostLikeHit";
                indexPostLikeHit.src = "/static/image/postLikeRed.png";

                let indexPostComment = document.createElement("img");
                indexPostComment.className = "indexPostComment";
                indexPostComment.src = "/static/image/postComment.png";

                let indexPostStore = document.createElement("img");
                indexPostStore.className = "indexpostStore";
                indexPostStore.src = "/static/image/postStore.png";

                let indexPostStoreHit = document.createElement("img");
                indexPostStoreHit.className = "indexPostStoreHit";
                indexPostStoreHit.src = "/static/image/postStoreBlack.png";
                
                indexPostLikeAndComment.appendChild(indexPostLike);
                indexPostLikeAndComment.appendChild(indexPostLikeHit);
                indexPostLikeAndComment.appendChild(indexPostComment);
                indexPostLikeAndComment.appendChild(indexPostStore);
                indexPostLikeAndComment.appendChild(indexPostStoreHit);
                
                let indexPostUserContentSection = document.createElement("div");
                indexPostUserContentSection.className = "indexPostUserContentSection";

                let indexPostUserName = document.createElement("span");
                indexPostUserName.className = "indexPostUserName";
                indexPostUserName.innerText = post.user_name;

                let indexPostContent = document.createElement("span");
                indexPostContent.className = "indexPostContent";
                indexPostContent.innerText = post.content;

                indexPostUserContentSection.appendChild(indexPostUserName);
                indexPostUserContentSection.appendChild(indexPostContent);
                postSect.appendChild(postBanner);
                postSect.appendChild(indexPostImage);
                postSect.appendChild(indexPostLikeAndComment);
                postSect.appendChild(indexPostUserContentSection);
                let commentSection = null;
                let commentLoading = false;

                indexPostComment.addEventListener("click", async function() {

                    if (commentLoading) {
                        return;
                    }

                    if (commentSection === null) {
                        commentLoading = true;

                        try {
                            commentSection = await createCommentSection(post.id);

                            postSect.appendChild(commentSection);

                        } catch (error) {
                            console.error("載入留言失敗:", error);
                            alert("載入留言失敗");
                        } finally {
                            commentLoading = false;
                        }

                        return;
                    }

                    if (commentSection.style.display === "none") {
                        commentSection.style.display = "flex";
                    } else {
                        commentSection.style.display = "none";
                    }
                });
                /*
                postSect.innerHTML = `
                    <div class = "postBanner"> 
                        <img class = "post_avatar" src="${post.avatar_url}">
                        ${post.display_name}
                    </div>
                    <img src="${post.image_url}" class = "indexPostImage">
                    <div class = "indexPostLikeAndComment">
                        <img class = "indexPostLike" src = "/static/image/postLike.png">
                        <img class = "indexPostLikeHit" src = "/static/image/postLikeRed.png">
                        <img class = "indexPostComment" src = "/static/image/postComment.png">
                        <img class = "indexpostStore" src = "/static/image/postStore.png">
                        <img class = "indexPostStoreHit" src = "/static/image/postStoreBlack.png">
                    </div>
                    <div class = "indexPostUserContentSection">
                        <div class="indexPostUserName"> ${post.user_name} </div>
                        <div class="indexPostContent"> ${post.content}</div>
                    </div>

                ` */
                if(post.is_liked){
                    indexPostLike.style.display = "none";
                    indexPostLikeHit.style.display = "block";
                }else{
                    indexPostLike.style.display = "block";
                    indexPostLikeHit.style.display = "none";
                }
                post_avatar.addEventListener("click", function() {
                    window.location.href = `/${post.user_name}`;
                })

                postContainer.appendChild(postSect);
                indexPostLike.addEventListener("click", async function () {
                    let formdata = new FormData();
                    formdata.append("post_id", post.id);
                    const likeResponse = await fetch("/api/post/like", {
                        method: "PATCH",
                        body: formdata
                    })
                    const likeResult = await likeResponse.json();
                    if(likeResult.ok){
                        indexPostLike.style.display = "none";
                        indexPostLikeHit.style.display = "block";
                    }
                })

                indexPostLikeHit.addEventListener("click", async function () {
                    let formdata = new FormData();
                    formdata.append("post_id", post.id);
                    const likeResponse = await fetch("/api/post/likeDelete", {
                        method: "PATCH",
                        body: formdata
                    })
                    const likeResult = await likeResponse.json();
                    if(likeResult.ok){
                        indexPostLike.style.display = "block";
                        indexPostLikeHit.style.display = "none";
                    }
                })
            });
        }
        nextCursor = result.nextCursor;
        hasMore = result.hasMore;
        if(hasMore == false){
            observer.disconnect();
        }
    }catch(error){
        console.log("載入貼文失敗", error);
    }finally{
        isLoading = false;
    }

}


function observeCallBack(entries){
    if(entries[0].isIntersecting){
        getFollowingPost();
    }
}


async function getUserInformation() {
    const response = await fetch("/api/user",{
        method: "GET"
    });
    const result = await response.json();
    /* result 裡面會裝 {"ok": True, "data": {"user_name": user_name, "display_name": display_name}} */
    const display_name = result.data.display_name;
    avatar_name.innerText = display_name;
    const avatar_url =result.data.avatar_url;
    userAvatar.src = avatar_url || "/static/image/avatar_default.png";
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



/* ######################## 好友狀態欄  ####################################### */

let friendStatusContainer = document.querySelector("#friendStatusContainer");

async function getFriendStatus() {
    const response = await fetch("/api/getFriendStatus",{
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        result.friends.forEach(friend=>{
            let friendBlock = `
            <div>
                <img class="friendStatusCircle" src=${friend.avatar_url}>
                <div class="friendStatusDisplayName"> ${friend.display_name} </div>
            </div>
            `
            friendStatusContainer.insertAdjacentHTML("beforeend", friendBlock);
            let friendPresent = friendStatusContainer.lastElementChild;
            let friend_img = friendPresent.querySelector("img");
            friend_img.addEventListener("click", function(){
                window.location.href = `/${friend.user_name}`;
            });
        })
    }
}



/* ############################################################################ */


userAvatar.addEventListener("click", async function(){
    const response = await fetch("/api/user",{
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        window.location.href = `/${result.data.user_name}`
    }
})






