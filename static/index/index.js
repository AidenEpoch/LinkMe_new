const avatar_name = document.querySelector("#user_name"); 
let postContainer = document.querySelector("#postContainer");

addEventListener("DOMContentLoaded", () => {
    getUserInformation();
    getFollowingPost();
})


async function getFollowingPost(){
    const response = await fetch("/api/indexPost", {
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