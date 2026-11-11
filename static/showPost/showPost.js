const messageClosePost = document.querySelector("#messageClosePostShow");
const messagePostShow = document.querySelector("#messagePostShow");
messageClosePost.addEventListener("click", closemessagePostShow);

function closemessagePostShow(){
    messagePostShow.close();
    document.body.style.overflow = "";
}
async function messageShowPost(post_id) {
    messageClosePost.style.display = "block";
    const response = await fetch(`/api/showPost/${post_id}`, {
        method: "GET"
    })
    const result = await response.json();
    messagePostShow.querySelectorAll(".messagePostSect").forEach(element => {
        element.remove();
    });
    let messagePostSection = document.createElement("div");
    let messagePostImg = document.createElement("div");
    let messagePostInfo = document.createElement("div");
    let messagePostName = document.createElement("div");
    let messagePostContent = document.createElement("p");
    let hr = document.createElement("hr");
    let messageLikeAndComment = document.createElement("div");
    messageLikeAndComment.className = "messagePostLikeAndComment";
    messageLikeAndComment.innerHTML = `
        <img class = "messagePostLike" src = "/static/image/postLike.png">
        <img class = "messagePostLikeHit" src = "/static/image/postLikeRed.png">
        <img class = "messagePostComment" src = "/static/image/postComment.png">
        <img class = "messagePostStore" src = "/static/image/postStore.png">
        <img class = "messagePostStoreHit" src = "/static/image/postStoreBlack.png">
    `
    messagePostName.className = "messagePostName";
    messagePostContent.className = "messagePostContent";
    messagePostInfo.className = "messagePostInfo";
    messagePostSection.className = "messagePostSect";
    messagePostImg.className = "messagePostImg";
    messagePostContent.innerText = result.content;
    messagePostName.innerText = result.name;
    messagePostImg.style.backgroundImage = `url(${result.img_url})`;
    messagePostImg.style.backgroundSize = "cover";
    messagePostImg.style.backgroundRepeat = "no-repeat";
    messagePostShow.appendChild(messagePostSection);
    messagePostSection.appendChild(messagePostImg);
    messagePostInfo.appendChild(messagePostName);
    messagePostInfo.appendChild(messagePostContent);
    messagePostSection.appendChild(messagePostInfo);
    messagePostInfo.appendChild(messageLikeAndComment);
    messagePostShow.showModal();
    document.body.style.overflow = "hidden";
}