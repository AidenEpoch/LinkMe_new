const avatar_name = document.querySelector("#user_name"); 

addEventListener("DOMContentLoaded", getUserInformation)




async function getUserInformation() {
    const response = await fetch("/api/user",{
        method: "GET"
    });
    const result = await response.json();
    /* result 裡面會裝 {"ok": True, "data": {"user_name": user_name, "display_name": display_name}} */
    const display_name = result.data.display_name;
    avatar_name.innerHTML = display_name;

}