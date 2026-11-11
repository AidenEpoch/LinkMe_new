addEventListener("DOMContentLoaded", ()=>{
    let messageBoard = document.querySelector("#messageBoard");
    const messageBtn = document.querySelector("#messageBlock");
    let leftNavShow = document.querySelector("#leftNavShow");
    let leftNavHidden = document.querySelector("#leftNavHidden");
    const messageCloseBtn = document.querySelector("#messageCloseBtn");
    const reminderContainer = document.querySelector("#reminderContainer");
    messageBtn.addEventListener("click", openMessageBoard);
    messageCloseBtn.addEventListener("click", closeMessageBoard);
    getReminder();

    function openMessageBoard(){
        isMessageOpen = true;
        messageBoard.style.display = "block";
        leftNavShow.style.display = "none";
        leftNavHidden.style.display = "none";
    }

    function closeMessageBoard(){
        isMessageOpen = false;
        messageBoard.style.display = "none";
        leftNavShow.style.display = "flex";
        leftNavHidden.style.display = "none";
    }

    async function getReminder() {
    const response = await fetch("/api/notificationGet", {
        method: "GET"
    });
    const result = await response.json();
    if(result.ok){
        result.notifications.forEach(notify=>{
            if(notify.is_read){
                return;
            }else{
                let notifyBlock = document.createElement("div");
                notifyBlock.className = "notifyBlock";
                let notifyContent = document.createElement("div");
                notifyContent.className = "notifyContent";
                let notifyAvatar = document.createElement("img");
                notifyAvatar.className = "notifyAvatar";
                if(notify.type == "follow_checking"){
                    let notifyAnswer = document.createElement("div");
                    notifyAnswer.className = "notifyAnswer";
                    let notifyAnswerAccept = document.createElement("div");
                    notifyAnswerAccept.className = "notifyAnswerAccept";
                    let notifyAnswerReject = document.createElement("div");
                    notifyAnswerReject.className = "notifyAnswerReject";
                    notifyAnswerAccept.innerText = "接受";
                    notifyAnswerReject.innerText = "拒絕";
                    let notifyAnswerAvatar = document.createElement("img");
                    notifyAnswerAvatar.className = "notifyAnswerAvatar";
                    notifyAnswerAvatar.src = notify.avatar_url;
                    let notifyAnswerName = document.createElement("div");
                    notifyAnswerName.className = "notifyAnswerName";
                    notifyAnswerName.innerText = notify.display_name + " 希望追蹤你";
                    notifyAnswer.appendChild(notifyAnswerAvatar);
                    notifyAnswer.appendChild(notifyAnswerName);
                    notifyAnswer.appendChild(notifyAnswerAccept);
                    notifyAnswer.appendChild(notifyAnswerReject);
                    notifyBlock.appendChild(notifyAnswer);
                    reminderContainer.appendChild(notifyBlock);

                    notifyAnswerAccept.addEventListener("click", async function(){
                        let formdata = new FormData();
                        formdata.append("receiver_id", notify.user_id);
                        formdata.append("actor_id", notify.actor_id);
                        formdata.append("notification_id", notify.id);
                        const response = await fetch("/api/private/follow", {
                            method: "PATCH",
                            body:formdata
                        })
                        const acceptResult = await response.json();

                        if(response.ok && acceptResult.ok){
                            window.location.reload();
                        }else{
                            alert(acceptResult.message || "接受追蹤申請失敗");
                        }
                    })

                    notifyAnswerReject.addEventListener("click", async function(){
                        let formdata = new FormData();

                        formdata.append("actor_id", notify.actor_id);

                        const response = await fetch("/api/private/reject", {
                            method: "PATCH",
                            body: formdata
                        });

                        const rejectResult = await response.json();

                        if(response.ok && rejectResult.ok){
                            window.location.reload();
                        }else{
                            alert(rejectResult.message || "拒絕追蹤申請失敗");
                        }
                    });
                }else{
                    if(notify.type == "follow"){
                        notifyContent.innerText = `${notify.display_name} 在追蹤你`;
                    }else if(notify.type == "like"){
                        notifyContent.innerText = `${notify.display_name} 讚了你的貼文`;
                    }else if(notify.type == "comment"){
                        notifyContent.innerText = `${notify.display_name} 在你的貼文留言`;
                    }
                    notifyAvatar.src = notify.avatar_url;
                    notifyBlock.appendChild(notifyAvatar);
                    notifyBlock.appendChild(notifyContent);


                    reminderContainer.appendChild(notifyBlock);
                    notifyBlock.addEventListener("click", readReminder);
                    async function readReminder() {
                        let formdata = new FormData();
                        formdata.append("note_id", notify.id);
                        const response = await fetch("/api/readNotification", {
                            method: "PATCH",
                            body: formdata
                        })
                        const result = await response.json();
                        if(result.ok){
                            if(notify.type == "follow"){
                                window.location.href = `/${encodeURIComponent(notify.user_name)}`;
                            }
                            else if(notify.type == "like" || notify.type == "comment"){
                                messageShowPost(notify.post_id);
                            }
                        }
                    }
                }
            }
        })
    }
}
})




