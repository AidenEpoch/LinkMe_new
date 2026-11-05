const avatar_name = document.querySelector("#user_name"); 
let postContainer = document.querySelector("#postContainer");
const sentinel = document.querySelector("#sentinel");


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
})


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
                postSect.innerHTML = `
                    <div class = "postBanner"> 發文者:  ${post.display_name}</div>
                    <img src="${post.image_url}">

                `
                postContainer.appendChild(postSect);
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
    avatar_name.innerHTML = display_name;

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


const userAvatar = document.querySelector("#userAvatar");
userAvatar.addEventListener("click", async function(){
    const response = await fetch("/api/user",{
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        window.location.href = `/${result.data.user_name}`
    }
})






