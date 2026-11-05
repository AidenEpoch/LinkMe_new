let searchMainShow = document.querySelector("#searchMainShow");
let searchInput = document.querySelector("#searchInput");
let searchIcon = document.querySelector("#searchIcon");
const returnBtn = document.querySelector("#returnBtn");
let searchContainer = document.querySelector("#searchContainer");
let recommendContainer = document.querySelector("#recommendContainer");
searchInput.addEventListener("click", openSearchResult);
returnBtn.addEventListener("click", closeSearchResult);
window.addEventListener("pageshow", closeSearchResult);


function openSearchResult(){
    returnBtn.style.display = "block";
    searchInput.style.marginLeft = "35px";
    searchInput.style.width = "70%";
    searchIcon.style.marginLeft = "35px";
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
