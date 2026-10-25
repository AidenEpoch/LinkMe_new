let avatar_name = document.querySelector("#avatar_name");
let readStore = document.querySelector("#readStoreBtn");
let editProfile = document.querySelector("#editProfileBtn");

addEventListener("DOMContentLoaded", ()=>{
    getUserInformation(); 
    getUserPosts();
});


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
        }else{
            readStore.style.display = "none";
            editProfile.style.display = "none";
        }
    }
}

async function getUserPosts() {
    const response = await fetch("/api/userGetPost", {
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
            image.src = post.image_key;
            image.alt = post.content || "貼文";
            image.loading = "lazy";

            postItem.appendChild(image);
            postContainer.append(postItem);
        });
    }
}



