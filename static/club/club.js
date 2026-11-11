
const clubList = document.querySelector("#clubListSection");
const clubSentinel = document.querySelector("#clubSentinel");
const clubLoading = document.querySelector("#clubLoading");
const clubSearchInput = document.querySelector("#clubSearchInput");
const myClubContainer = document.querySelector("#myClubContainer");

const createClubBtn = document.querySelector("#createClubBtn");
const createClubDialog = document.querySelector("#createClubDialog");
const createClubForm = document.querySelector("#createClubForm");
const cancelClubBtn = document.querySelector("#cancelClubBtn");
const submitClubBtn = document.querySelector("#submitClubBtn");

let clubNextCursor = null;
let clubHasMore = true;
let clubIsLoading = false;
let clubKeyword = "";
let clubSearchTimer = null;
let clubGeneration = 0;
let clubController = null;


// API 請求
async function clubRequest(url, options = {}) {
    const response = await fetch(url, options);
    const result = await response.json();

    if (!response.ok || !result.ok) {
        throw new Error(result.message || "操作失敗");
    }

    return result;
}


// 圖片載入失敗時使用預設圖
function setClubImage(img, url) {
    img.src = url || "/static/image/avatar_default.png";

    img.onerror = function() {
        img.onerror = null;
        img.src = "/static/image/avatar_default.png";
    };
}


// 建立社群卡片
function createClubCard(club) {
    const card = document.createElement("div");
    card.className = "clubCard";

    const image = document.createElement("img");
    image.className = "clubCover";
    image.alt = club.name;
    setClubImage(image, club.img_url);

    const info = document.createElement("div");
    info.className = "clubCardInfo";

    const name = document.createElement("h3");
    name.textContent = club.name;

    const type = document.createElement("span");
    type.className = "clubType";
    type.textContent = club.type || "一般社群";

    const description = document.createElement("p");
    description.className = "clubDescription";
    description.textContent = club.description || "尚無社群簡介";

    const members = document.createElement("span");
    members.className = "clubMemberCount";
    members.textContent = `${club.member_count} 位成員`;

    info.append(name, type, description, members);

    const button = document.createElement("button");
    button.className = "clubJoinBtn";

    function updateButton() {
        if (club.my_role === "owner") {
            button.textContent = "建立者";
            button.disabled = true;
            button.classList.add("clubOwnerBtn");
        } else if (club.is_member) {
            button.textContent = "退出社群";
            button.disabled = false;
            button.classList.remove("clubOwnerBtn");
        } else {
            button.textContent = "加入社群";
            button.disabled = false;
            button.classList.remove("clubOwnerBtn");
        }
    }

    updateButton();

    button.addEventListener("click", async () => {
        if (club.my_role === "owner") return;

        button.disabled = true;

        try {
            const wasMember = club.is_member;

            if (wasMember) {
                await clubRequest(
                    `/api/clubs/${club.id}/leave`,
                    { method: "DELETE" }
                );
            } else {
                await clubRequest(
                    `/api/clubs/${club.id}/join`,
                    { method: "POST" }
                );
            }

            club.is_member = !wasMember;
            club.my_role = club.is_member ? "member" : null;

            // 從伺服器重新取得成員數，
            // 避免重複加入或其他使用者操作造成數字錯誤
            resetClubs();
            await loadMyClubs();

        } catch (error) {
            alert(error.message);
            updateButton();
        }
    });

    card.append(image, info, button);

    return card;
}


// 顯示空列表訊息
function showClubEmpty(message) {
    clubList.replaceChildren();

    const empty = document.createElement("div");
    empty.className = "clubEmpty";
    empty.textContent = message;

    clubList.appendChild(empty);
}


// 載入社群列表
async function loadClubs() {
    if (clubIsLoading || !clubHasMore) {
        return;
    }

    clubIsLoading = true;
    clubLoading.style.display = "block";
    clubLoading.textContent = "載入中...";

    const generation = clubGeneration;
    const controller = new AbortController();
    clubController = controller;

    let failed = false;

    try {
        const params = new URLSearchParams({
            limit: "12",
            keyword: clubKeyword
        });

        if (clubNextCursor !== null) {
            params.set("cursor", clubNextCursor);
        }

        const result = await clubRequest(
            `/api/clubs?${params.toString()}`,
            { signal: controller.signal }
        );

        if (generation !== clubGeneration) return;

        result.clubs.forEach(club => {
            clubList.appendChild(createClubCard(club));
        });

        clubNextCursor = result.nextCursor;
        clubHasMore = result.hasMore;

        if (!clubHasMore) {
            clubObserver.unobserve(clubSentinel);
        }

        if (!clubList.children.length) {
            showClubEmpty(
                clubKeyword
                    ? "找不到符合條件的社群"
                    : "目前還沒有社群，快來建立第一個吧！"
            );
        }

    } catch (error) {
        if (generation !== clubGeneration) return;

        if (error.name !== "AbortError") {
            failed = true;
            console.error("載入社群失敗:", error);
            clubLoading.textContent = "載入失敗，請稍後重試";
        }

    } finally {
        if (generation === clubGeneration) {
            clubIsLoading = false;
            clubController = null;

            if (!failed) {
                clubLoading.style.display = "none";
            }

            // 若 Sentinel 仍在畫面中，繼續載入下一批
            if (
                !failed &&
                clubHasMore &&
                clubList.children.length > 0 &&
                clubSentinel.getBoundingClientRect().top <
                    window.innerHeight + 300
            ) {
                loadClubs();
            }
        }
    }
}


// 重設社群列表
function resetClubs() {
    clubGeneration++;

    if (clubController) {
        clubController.abort();
        clubController = null;
    }

    clubIsLoading = false;
    clubHasMore = true;
    clubNextCursor = null;

    clubList.replaceChildren();

    clubObserver.observe(clubSentinel);
    loadClubs();
}


// 無限捲動
const clubObserver = new IntersectionObserver(
    entries => {
        if (entries[0].isIntersecting) {
            loadClubs();
        }
    },
    {
        root: null,
        rootMargin: "300px 0px",
        threshold: 0
    }
);


// 搜尋社群
clubSearchInput.addEventListener("input", () => {
    clearTimeout(clubSearchTimer);

    clubSearchTimer = setTimeout(() => {
        clubKeyword = clubSearchInput.value.trim();
        resetClubs();
    }, 300);
});


// 取得我的社群
async function loadMyClubs() {
    try {
        const result = await clubRequest("/api/clubs/mine");

        myClubContainer.replaceChildren();

        if (result.clubs.length === 0) {
            myClubContainer.textContent = "尚未加入任何社群";
            return;
        }

        result.clubs.forEach(club => {
            const item = document.createElement("div");
            item.className = "myClubItem";

            const image = document.createElement("img");
            image.className = "myClubImage";
            image.alt = club.name;
            setClubImage(image, club.img_url);

            const text = document.createElement("div");
            text.className = "myClubText";

            const name = document.createElement("strong");
            name.className = "myClubName";
            name.textContent = club.name;

            const role = document.createElement("span");
            role.className = "myClubRole";

            const roleNames = {
                owner: "建立者",
                admin: "管理員",
                member: "成員"
            };

            role.textContent = roleNames[club.role] || "成員";

            text.append(name, role);
            item.append(image, text);

            myClubContainer.appendChild(item);
        });

    } catch (error) {
        console.error("取得我的社群失敗:", error);
    }
}


// 開啟建立社群視窗
createClubBtn.addEventListener("click", () => {
    createClubDialog.showModal();
});


// 關閉建立社群視窗
cancelClubBtn.addEventListener("click", () => {
    createClubDialog.close();
});


// 提交建立社群
createClubForm.addEventListener("submit", async event => {
    event.preventDefault();

    const data = new FormData(createClubForm);

    const name = String(data.get("name") || "").trim();

    if (!name) {
        alert("請輸入社群名稱");
        return;
    }

    submitClubBtn.disabled = true;

    try {
        const result = await clubRequest("/api/clubs", {
            method: "POST",
            body: data
        });

        alert(result.message);

        createClubForm.reset();
        createClubDialog.close();

        resetClubs();
        await loadMyClubs();

    } catch (error) {
        alert(error.message);
    } finally {
        submitClubBtn.disabled = false;
    }
});


// 初始化
clubObserver.observe(clubSentinel);
loadClubs();
loadMyClubs();
