
document.addEventListener("DOMContentLoaded", () => {

    const chatBox = document.querySelector(".chatBox");
    const chatNotificationDot = document.querySelector("#chatNotificationDot");
    const chatWindow = document.querySelector("#chatWindow");
    const chatCloseBtn = document.querySelector("#chatCloseBtn");




const chatConversationList = document.querySelector(
    "#chatConversationList"
);

const chatMainHeader = document.querySelector("#chatMainHeader");
const chatMessages = document.querySelector("#chatMessages");
const chatMessageInput = document.querySelector("#chatMessageInput");
const chatSendBtn = document.querySelector("#chatSendBtn");
const chatInputForm = document.querySelector("#chatInputForm");

// 目前登入的使用者 ID
// 目前正在查看的對話 ID
let currentConversationId = null;

// 目前登入的使用者 ID
let currentUserId = null;

// WebSocket 連線
let chatWs = null;


let messageLoadVersion = 0;




window.testChatDisconnect = function () {
    if (chatWs && chatWs.readyState === WebSocket.OPEN) {
        chatWs.close();
        console.log("測試：主動關閉 WebSocket");
    } else {
        console.log("目前 WebSocket 尚未連線");
    }
};









async function loadCurrentUser() {

    const response = await fetch("/api/chat/me");

    if (!response.ok) {
        throw new Error("無法取得登入使用者");
    }

    const data = await response.json();

    if (!data.ok) {
        throw new Error("使用者尚未登入");
    }

    currentUserId = Number(data.user_id);
}


function connectChatWebSocket() {

    // 避免重複建立連線
    if (
        chatWs &&
        (
            chatWs.readyState === WebSocket.OPEN ||
            chatWs.readyState === WebSocket.CONNECTING
        )
    ) {
        return;
    }

    const protocol =
        location.protocol === "https:" ? "wss:" : "ws:";

    chatWs = new WebSocket(
        `${protocol}//${location.host}/ws/chat`
    );

    
chatWs.onopen = async () => {

    console.log("LinkMe WebSocket 已連線");

    // 重新取得最新聊天列表
    await loadConversations();

    // 如果目前有選擇對話，重新取得聊天紀錄
    
    if (
        chatWindow.style.display === "flex" &&
        currentConversationId !== null
    ) {
        const conversationId = currentConversationId;
        const username = chatMainHeader.textContent;

        await loadMessages(conversationId, username);
    }


};


    chatWs.onmessage = (event) => {

        const data = JSON.parse(event.data);

        if (!data.ok) {
            console.error("聊天錯誤：", data.message);
            return;
        }

        

if (data.type === "new_message") {

    const message = data.message;

    // 更新左側聊天列表的最新訊息
    updateConversationPreview(message);

    
const isCurrentConversation =
    chatWindow.style.display === "flex" &&
    currentConversationId !== null &&
    Number(message.conversation_id) ===
    Number(currentConversationId);


    // 如果正在查看這個對話，顯示訊息氣泡
    if (isCurrentConversation) {
        appendChatMessage(message);
    }

    // 只有別人傳送的訊息才需要計算未讀
    if (Number(message.sender_id) !== currentUserId) {

        if (!isCurrentConversation) {
            increaseUnreadCount(message.conversation_id);
        } else {
            // 正在查看的對話，直接標記為已讀
            markConversationRead(message.conversation_id);
        }
    }
}


    };

    chatWs.onerror = (error) => {
        console.error("WebSocket 發生錯誤：", error);
    };

    
    chatWs.onclose = () => {
        console.log("LinkMe WebSocket 已中斷");

        // 3 秒後嘗試重新連線
        setTimeout(() => {
            console.log("正在重新連線 LinkMe WebSocket...");
            connectChatWebSocket();
        }, 3000);
    };

}


// 從後端取得聊天列表
async function loadConversations() {

    chatConversationList.textContent = "載入中...";

    try {
        const response = await fetch(
            "/api/chat/conversations"
        );

        if (!response.ok) {
            throw new Error("無法取得聊天列表");
        }

        const data = await response.json();

        if (!data.ok) {
            throw new Error("取得聊天列表失敗");
        }

        renderConversations(data.conversations);

    } catch (error) {
        console.error("聊天列表載入失敗：", error);

        chatConversationList.textContent =
            "聊天列表載入失敗";
    }
}


function updateChatNotificationDot() {
    const badges = chatConversationList.querySelectorAll(
        ".chatUnreadBadge"
    );

    const hasUnread = Array.from(badges).some(badge => {
        return Number(badge.textContent) > 0;
    });

    chatNotificationDot.style.display = hasUnread
        ? "block"
        : "none";
}



// 將聊天列表顯示在網頁上
function renderConversations(conversations) {

    chatConversationList.replaceChildren();

    if (conversations.length === 0) {
        chatConversationList.textContent =
            "目前沒有聊天紀錄";
        return;
    }

    conversations.forEach(conversation => {

        const item = document.createElement("div");
        item.className = "chatConversationItem";
        item.dataset.conversationId = conversation.conversation_id;

        const username = document.createElement("div");
        username.className = "chatConversationName";

        // 依照目前 API 的欄位名稱取得對方名稱
        username.textContent =
            conversation.display_name ??
            conversation.user_name ??
            `使用者 ${conversation.other_user_id}`;

        const preview = document.createElement("div");
        preview.className = "chatConversationPreview";

        preview.textContent =
            conversation.last_message ?? "開始聊天吧！";
        
        
        const unreadBadge = document.createElement("span");
        unreadBadge.className = "chatUnreadBadge";
        unreadBadge.textContent = conversation.unread_count;

        // 沒有未讀訊息時，隱藏紅色數字
        if (Number(conversation.unread_count) === 0) {
            unreadBadge.style.display = "none";
        }


        item.append(username, preview, unreadBadge);
        // 點擊聊天對象
item.addEventListener("click", () => {

    // 清除其他聊天對象的選取樣式
    document.querySelectorAll(".chatConversationItem")
        .forEach(element => {
            element.classList.remove("active");
        });

    // 標示目前選取的聊天對象
    item.classList.add("active");

    // 載入該對話的歷史訊息
    loadMessages(
    conversation.conversation_id,
    username.textContent
    );

});

        chatConversationList.appendChild(item);

    });
    updateChatNotificationDot();
}



function updateConversationPreview(message) {

    // 找出目前聊天列表中的對應對話
    const item = Array.from(
        chatConversationList.querySelectorAll(".chatConversationItem")
    ).find(element =>
        element.dataset.conversationId ===
        String(message.conversation_id)
    );

    if (!item) {
        return;
    }

    // 找到最新訊息預覽區域
    const preview = item.querySelector(
        ".chatConversationPreview"
    );

    if (preview) {
        preview.textContent = message.content;
    }

    // 將最新有訊息的對話移到列表最上方
    chatConversationList.prepend(item);
}


function increaseUnreadCount(conversationId) {

    const item = Array.from(
        chatConversationList.querySelectorAll(
            ".chatConversationItem"
        )
    ).find(element =>
        element.dataset.conversationId ===
        String(conversationId)
    );

    if (!item) {
        return;
    }

    const badge = item.querySelector(".chatUnreadBadge");

    if (!badge) {
        return;
    }

    const currentCount = Number(badge.textContent) || 0;

    badge.textContent = currentCount + 1;
    badge.style.display = "flex";
    updateChatNotificationDot();
}



async function markConversationRead(conversationId) {

    try {
        const response = await fetch(
            `/api/chat/conversations/${conversationId}/read`,
            {
                method: "POST"
            }
        );

        if (!response.ok) {
            throw new Error("標記已讀失敗");
        }

        const data = await response.json();

        if (!data.ok) {
            throw new Error("標記已讀失敗");
        }

        // 找出對應的聊天列表項目
        const item = Array.from(
            chatConversationList.querySelectorAll(
                ".chatConversationItem"
            )
        ).find(element =>
            element.dataset.conversationId ===
            String(conversationId)
        );

        if (item) {
            const badge = item.querySelector(
                ".chatUnreadBadge"
            );

            if (badge) {
                badge.textContent = "0";
                badge.style.display = "none";
                updateChatNotificationDot();
            }
        }

    } catch (error) {
        console.error("標記已讀失敗：", error);
    }
}



async function loadMessages(conversationId, username) {


    const requestVersion = ++messageLoadVersion;

    currentConversationId = conversationId;

    // 顯示目前選取的聊天對象
    chatMainHeader.textContent = username;

    // 清除上一個對話的訊息
    chatMessages.replaceChildren();
    chatMessages.textContent = "載入訊息中...";

    // 載入期間先禁止傳送
    chatMessageInput.disabled = true;
    chatSendBtn.disabled = true;

    try {
        const response = await fetch(
            `/api/chat/conversations/${conversationId}/messages`
        );

        if (!response.ok) {
            throw new Error("無法取得歷史訊息");
        }

        const data = await response.json();

        if (!data.ok) {
            throw new Error("取得歷史訊息失敗");
        }

        // 避免快速切換對話時，舊請求覆蓋新畫面
        
        
        if (
            requestVersion !== messageLoadVersion ||
            Number(currentConversationId) !== Number(conversationId) ||
            chatWindow.style.display !== "flex"
        ) {
            return;
        }



        
        renderMessages(data.messages);

        chatMessageInput.disabled = false;
        chatSendBtn.disabled = false;

        // 成功載入並顯示歷史訊息後，標記為已讀
        await markConversationRead(conversationId);


    } catch (error) {

        if (currentConversationId !== conversationId ||
        Number(currentConversationId) !== Number(conversationId) ||
        chatWindow.style.display !== "flex") {
            return;
        }

        console.error("載入歷史訊息失敗：", error);
        chatMessages.textContent = "無法載入聊天紀錄";
    }
}



function renderMessages(messages) {

    // 保留載入期間 WebSocket 已經收到的訊息
    const existingMessages = new Map();

    chatMessages.querySelectorAll(".chatMessage").forEach(element => {
        const messageId = element.dataset.messageId;

        if (messageId) {
            existingMessages.set(messageId, element);
        }
    });

    // 清空舊畫面
    chatMessages.replaceChildren();

    // 依照訊息 ID 由小到大排序
    const sortedMessages = [...messages].sort(
        (a, b) => Number(a.id) - Number(b.id)
    );

    // 先顯示歷史訊息
    sortedMessages.forEach(message => {

        const messageId = String(message.id);

        // 如果 WebSocket 已經顯示過，就使用原本的元素
        if (existingMessages.has(messageId)) {
            chatMessages.appendChild(
                existingMessages.get(messageId)
            );
            existingMessages.delete(messageId);
        } else {
            appendChatMessage(message);
        }

    });

    // 補上歷史資料載入期間收到的新訊息
    const remainingMessages = Array.from(
        existingMessages.values()
    ).sort(
        (a, b) =>
            Number(a.dataset.messageId) -
            Number(b.dataset.messageId)
    );

    remainingMessages.forEach(element => {
        chatMessages.appendChild(element);
    });

    chatMessages.scrollTop = chatMessages.scrollHeight;
}




function appendChatMessage(message) {

    // 檢查這則訊息是否已經顯示過
    const existingMessage = Array.from(
        chatMessages.querySelectorAll(".chatMessage")
    ).find(element =>
        element.dataset.messageId === String(message.id)
    );

    // 已經存在就不重複新增
    if (existingMessage) {
        return;
    }

    const messageElement = document.createElement("div");

    messageElement.classList.add("chatMessage");

    // 記錄訊息 ID
    messageElement.dataset.messageId = message.id;

    if (Number(message.sender_id) === currentUserId) {
        messageElement.classList.add("mine");
    } else {
        messageElement.classList.add("other");
    }

    messageElement.textContent = message.content;

    chatMessages.appendChild(messageElement);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}



    

async function openChat() {

    chatWindow.style.display = "flex";

    try {
        await loadCurrentUser();

        // 建立即時聊天連線
        connectChatWebSocket();

        await loadConversations();

    } catch (error) {
        console.error("聊天室初始化失敗：", error);
        chatConversationList.textContent =
            "無法載入聊天室，請確認登入狀態";
    }
}


window.openChatConversation = async function(conversationId) {

    // 開啟聊天室並載入聊天列表
    await openChat();

    // 找到指定的聊天對象
    const item = Array.from(
        chatConversationList.querySelectorAll(".chatConversationItem")
    ).find(element =>
        element.dataset.conversationId === String(conversationId)
    );

    if (!item) {
        console.error("找不到指定的聊天對話：", conversationId);
        return;
    }

    // 模擬點擊該聊天對象
    item.click();
};




    // 關閉聊天室
    function closeChat() {

    
    messageLoadVersion++;

    // 關閉聊天室視窗
    chatWindow.style.display = "none";

    // 清除目前選擇的對話
    currentConversationId = null;

    // 重設右側聊天室標題
    chatMainHeader.textContent = "請選擇一個聊天對象";

    // 清除之前顯示的訊息
    chatMessages.replaceChildren();

    // 禁止在尚未選擇對話時傳送訊息
    chatMessageInput.value = "";
    chatMessageInput.disabled = true;
    chatSendBtn.disabled = true;

}


async function initializeChatNotification() {
    try {
        await loadCurrentUser();

        // 網頁載入時，先檢查 MySQL 中的未讀訊息
        await loadConversations();

        // 建立 WebSocket，持續接收新訊息
        connectChatWebSocket();

    } catch (error) {
        console.error("聊天通知初始化失敗：", error);
    }
}

initializeChatNotification();



    // 點擊右下角訊息按鈕
    chatBox.addEventListener("click", openChat);

    // 點擊聊天室關閉按鈕
    chatCloseBtn.addEventListener("click", closeChat);


    chatInputForm.addEventListener("submit", (event) => {

    event.preventDefault();

    const content = chatMessageInput.value.trim();

    if (!content || currentConversationId === null) {
        return;
    }

    // 確認 WebSocket 已連線
    if (!chatWs || chatWs.readyState !== WebSocket.OPEN) {
        alert("聊天連線尚未建立，請稍後再試");
        return;
    }

    chatWs.send(JSON.stringify({
        conversation_id: currentConversationId,
        content: content
    }));

    // 清空輸入框
    chatMessageInput.value = "";
});
});



