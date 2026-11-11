let searchMainShow = document.querySelector("#searchMainShow");
let searchInput = document.querySelector("#searchInput");
let searchIcon = document.querySelector("#searchIcon");
const returnBtn = document.querySelector("#returnBtn");
let searchContainer = document.querySelector("#searchContainer");
let recommendContainer = document.querySelector("#recommendContainer");
let searchSentinel = document.querySelector("#searchSentinel");
let searchPostShow = document.querySelector("#searchPostShow");
let searchClosePostShow = document.querySelector("#searchClosePostShow");
searchClosePostShow.addEventListener("click", closeSearchPostShow);
searchInput.addEventListener("click", openSearchResult);
returnBtn.addEventListener("click", closeSearchResult);
window.addEventListener("pageshow", closeSearchResult);

const options = {
    root: null,
    rootMargin: "300px 0px",
    threshold: 0
}

function closeSearchPostShow(){
    searchPostShow.close();
    document.body.style.overflow = "";
}

function searchObserveCallBack(entries){
    if(entries[0].isIntersecting){
        getSearchFollowingPost();
    }
}
let observer = new IntersectionObserver(searchObserveCallBack, options);

document.addEventListener("DOMContentLoaded", ()=>{
    observer.observe(searchSentinel)
});

function openSearchResult(){
    returnBtn.style.display = "block";
    /*searchInput.style.marginLeft = "35px"; */
    searchInput.style.width = "60%";
    searchIcon.style.marginLeft = "0px";
    searchContainer.style.display = "flex";
    recommendContainer.style.display = "none";
}

function closeSearchResult(){
    clearTimeout(searchTimer);
    if(searchController){
        searchController.abort();
        searchController = null;
    }
    returnBtn.style.display = "none";
    searchInput.style.marginLeft = "";
    searchIcon.style.marginLeft = "";
    searchInput.style.width = "";
    searchContainer.style.display = "none";
    recommendContainer.style.display = "grid";
    searchInput.value = "";
    searchContainer.replaceChildren();
}

/* ###########################  以下為搜尋功能 #############################  */
searchInput.addEventListener("input", inputWords);


let searchTimer = null;   
let searchController = null;

async function inputWords() {
    clearTimeout(searchTimer);
    if(searchController){
        searchController.abort();
    }

    const keyword = searchInput.value.trim();
    
    if(keyword == ""){
        searchContainer.replaceChildren();
        return;
    }
    searchTimer = setTimeout(async function(){
        const controller = new AbortController();
        searchController = controller;

        try{
            const response = await fetch(`/api/searchResult?keyword=${encodeURIComponent(keyword)}`,
                {method: "GET",
                 signal: controller.signal   
                }
            )
            if(response.ok){
                const result = await response.json();
                if(searchInput.value.trim() != keyword){
                    return;
                }
                searchContainer.replaceChildren();
                result.data.forEach(user => {
                    const userBlock = document.createElement("div");
                    const userAvatar = document.createElement("img");
                    const userName = document.createElement("div");
                    userName.className = "userName";
                    userAvatar.className = "userAvatar";
                    userBlock.className = "userBlock";
                    userName.innerText = user.display_name;
                    console.log(user.avatar_url);
                    userAvatar.src= user.avatar_url || "/static/image/avatar_default.png";
                    userBlock.appendChild(userAvatar);
                    userBlock.appendChild(userName);
                    searchContainer.appendChild(userBlock);
                    
                    userBlock.addEventListener("mouseenter", function(){
                        userBlock.style.backgroundColor = "rgb(221, 219, 219)"
                        userBlock.style.borderRadius = "20px";
                    })

                    userBlock.addEventListener("mouseleave", function(){
                        userBlock.style.backgroundColor = "";
                        userBlock.style.borderRadius = "";
                    })

                    userBlock.addEventListener("click", function(){
                        window.location.href = `/${encodeURIComponent(user.user_name)}`;
                    })
                });
            }
        }catch(error){
            if (error.name !== "AbortError") {
                console.error("搜尋發生錯誤:", error);
            }
        }
    }, 300)
    
}



/* ######################################################################## */

/* ############################## 取得搜尋頁面的貼文 ########################################## */



let searchHasMore = true;
let searchIsLoading = false;
let searchNextCursor = null;

async function getSearchFollowingPost(){

    if((searchHasMore == false) || (searchIsLoading == true)){
        return;
    }
    searchIsLoading = true;
    try{
        let url = "/api/searchPost";
        if(searchNextCursor != null){
            const params = new URLSearchParams(searchNextCursor);
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
                let searchPostSect = document.createElement("img");
                searchPostSect.className = "searchPostSect";
                searchPostSect.src = post.image_url;
                recommendContainer.appendChild(searchPostSect);
                searchPostSect.addEventListener("click", function(){
                    showSearchPost(post.id)
                });
            });
        }
        searchNextCursor = result.nextCursor;
        searchHasMore = result.hasMore;
        if(searchHasMore == false){
            observer.disconnect();
        }
    }catch(error){
        console.log("載入貼文失敗", error);
    }finally{
        searchIsLoading = false;
    }

}

async function showSearchPost(post_id) {
    searchClosePostShow.style.display = "block";
    const response = await fetch(`/api/showPost/${post_id}`, {
        method: "GET"
    })
    const result = await response.json();
    searchPostShow.querySelectorAll(".searchpostSect").forEach(element => {
        element.remove();
    });
    let postSection = document.createElement("div");
    let postImg = document.createElement("div");
    let postInfo = document.createElement("div");
    let postName = document.createElement("div");
    let postContent = document.createElement("p");
    let hr = document.createElement("hr");
    let likeAndComment = document.createElement("div");
    likeAndComment.className = "searchpostLikeAndComment";
    
    let searchpostLike = document.createElement("img");
    searchpostLike.className = "searchpostLike";
    searchpostLike.src = "/static/image/postLike.png";

    let searchpostLikeHit = document.createElement("img");
    searchpostLikeHit.className = "searchpostLikeHit";
    searchpostLikeHit.src = "/static/image/postLikeRed.png";

    let searchpostComment = document.createElement("img");
    searchpostComment.className = "searchpostComment";
    searchpostComment.src = "/static/image/postComment.png";

    let searchpostStore = document.createElement("img");
    searchpostStore.className = "searchpostStore";
    searchpostStore.src = "/static/image/postStore.png";

    let searchpostStoreHit = document.createElement("img");
    searchpostStoreHit.className = "searchpostStoreHit";
    searchpostStoreHit.src = "/static/image/postStoreBlack.png";

    likeAndComment.appendChild(searchpostLike);
    likeAndComment.appendChild(searchpostLikeHit);
    likeAndComment.appendChild(searchpostComment);
    likeAndComment.appendChild(searchpostStore);
    likeAndComment.appendChild(searchpostStoreHit);
    searchpostStore.style.display = "block";
    searchpostStoreHit.style.display = "none";

    if(result.isLike){
        searchpostLike.style.display = "none";
        searchpostLikeHit.style.display = "block";
    }else{
        searchpostLike.style.display = "block";
        searchpostLikeHit.style.display = "none";
    }
    
    postName.className = "searchpostName";
    postContent.className = "searchpostContent";
    postInfo.className = "searchpostInfo";
    postSection.className = "searchpostSect";
    postImg.className = "searchpostImg";
    postContent.innerText = result.content;
    postName.innerText = result.name;
    postImg.style.backgroundImage = `url(${result.img_url})`;
    postImg.style.backgroundSize = "cover";
    postImg.style.backgroundRepeat = "no-repeat";
    postImg.style.objectFit = "cover";
    postImg.style.objectPosition = "center";
    searchPostShow.appendChild(postSection);
    postSection.appendChild(postImg);
    postInfo.appendChild(postName);
    postInfo.appendChild(postContent);
    postSection.appendChild(postInfo);
    postInfo.appendChild(likeAndComment);

    const commentSection = await createCommentSection(post_id);

    commentSection.style.display = "none";
    postInfo.appendChild(commentSection);

    searchpostComment.addEventListener("click", function() {
        const isHidden = commentSection.style.display === "none";

        commentSection.style.display = isHidden ? "flex" : "none";
    });

    searchPostShow.showModal();
    document.body.style.overflow = "hidden";

    let formdata = new FormData();
    formdata.append("post_id", post_id);
    searchpostLike.addEventListener("click", async function() {
        const response = await fetch("/api/post/like", {
            method: "PATCH",
            body: formdata
        })
        const result = await response.json();
        if(result.ok){
            searchpostLike.style.display = "none";
            searchpostLikeHit.style.display = "block";
        }

    })


    searchpostLikeHit.addEventListener("click", async function () {
        const response = await fetch("/api/post/likeDelete", {
            method: "PATCH",
            body: formdata
        })
        const result = await response.json();
        if(result.ok){
            searchpostLike.style.display = "block";
            searchpostLikeHit.style.display = "none";
        }
    })

    searchpostStore.addEventListener("click", function() {
        searchpostStore.style.display = "none";
        searchpostStoreHit.style.display = "block";
    });

    searchpostStoreHit.addEventListener("click", function() {
        searchpostStore.style.display = "block";
        searchpostStoreHit.style.display = "none";
    });

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
                    try {
                        const response = await fetch(
                            `/api/post/comments/${comment.id}`,
                            { method: "DELETE" }
                        );

                        const result = await response.json();

                        if (!response.ok || !result.ok) {
                            throw new Error(result.message || "刪除失敗");
                        }

                        await loadComments();
                    } catch (error) {
                        alert(error.message);
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
                throw new Error(result.message || "留言失敗");
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
        console.error(error);
    }

    return section;
}


/* ########################################################################################### */
