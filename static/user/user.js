let avatar_name = document.querySelector("#avatar_name");
let readStore = document.querySelector("#readStoreBtn");
let editProfile = document.querySelector("#editProfileBtn");

addEventListener("DOMContentLoaded", getUserInformation);


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



