addEventListener("DOMContentLoaded", ()=>{
    let messageBoard = document.querySelector("#messageBoard");
    const messageBtn = document.querySelector("#messageBlock");
    let leftNavShow = document.querySelector("#leftNavShow");
    let leftNavHidden = document.querySelector("#leftNavHidden");
    const messageCloseBtn = document.querySelector("#messageCloseBtn");
    messageBtn.addEventListener("click", openMessageBoard);
    messageCloseBtn.addEventListener("click", closeMessageBoard);

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

})

async function getReminder() {
    const response = await fetch("/api/")
}

