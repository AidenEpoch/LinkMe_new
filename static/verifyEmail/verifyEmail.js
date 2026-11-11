
const inputs = Array.from(
    document.querySelectorAll("#codeInputs input")
);

const verifyBtn = document.querySelector("#verifyBtn");
const resendBtn = document.querySelector("#resendBtn");
const message = document.querySelector("#message");
const emailDisplay = document.querySelector("#emailDisplay");

const params = new URLSearchParams(window.location.search);
const email = params.get("email") || "";

emailDisplay.textContent = email;

function showMessage(text, success = false) {
    message.textContent = text;
    message.classList.toggle("success", success);
}

function getCode() {
    return inputs.map(input => input.value).join("");
}

function fillCode(value, startIndex = 0) {
    const digits = value.replace(/\D/g, "").slice(0, 6 - startIndex);

    digits.split("").forEach((digit, offset) => {
        inputs[startIndex + offset].value = digit;
    });

    const nextIndex = Math.min(startIndex + digits.length, 5);
    inputs[nextIndex].focus();
}

inputs.forEach((input, index) => {
    input.addEventListener("input", () => {
        const value = input.value.replace(/\D/g, "");

        if (value.length > 1) {
            input.value = "";
            fillCode(value, index);
            return;
        }

        input.value = value;

        if (value && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }
    });

    input.addEventListener("keydown", event => {
        if (event.key === "Backspace" && !input.value && index > 0) {
            inputs[index - 1].focus();
        }

        if (event.key === "Enter") {
            verifyEmail();
        }
    });

    input.addEventListener("paste", event => {
        event.preventDefault();

        const pasted = event.clipboardData.getData("text");
        fillCode(pasted, index);
    });
});

async function verifyEmail() {
    const code = getCode();

    if (!email) {
        showMessage("找不到 Email，請重新註冊或返回登入頁面");
        return;
    }

    if (!/^\d{6}$/.test(code)) {
        showMessage("請輸入完整的六位數驗證碼");
        return;
    }

    verifyBtn.disabled = true;
    showMessage("");

    try {
        const response = await fetch("/api/verify-email", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, code })
        });

        const result = await response.json();

        if (!response.ok || !result.ok) {
            showMessage(result.message || "驗證失敗");
            return;
        }

        showMessage("Email 驗證成功！即將返回登入頁面", true);

        setTimeout(() => {
            window.location.href = "/";
        }, 1500);

    } catch (error) {
        showMessage("網路連線異常，請稍後再試");
    } finally {
        verifyBtn.disabled = false;
    }
}

let cooldownInterval = null;

function startCooldown(seconds) {
    clearInterval(cooldownInterval);

    let remaining = Math.max(0, Math.ceil(seconds));

    resendBtn.disabled = true;

    const update = () => {
        if (remaining <= 0) {
            clearInterval(cooldownInterval);
            resendBtn.disabled = false;
            resendBtn.textContent = "重新寄送";
            return;
        }

        resendBtn.textContent = `重新寄送 (${remaining}s)`;
        remaining -= 1;
    };

    update();
    cooldownInterval = setInterval(update, 1000);
}

async function resendVerification() {
    if (!email) {
        showMessage("找不到 Email");
        return;
    }

    resendBtn.disabled = true;
    showMessage("");

    try {
        const response = await fetch("/api/resend-verification", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email })
        });

        const result = await response.json();

        if (response.status === 429) {
            showMessage(result.message || "請稍後再試");
            startCooldown(result.retryAfter || 60);
            return;
        }

        if (!response.ok || !result.ok) {
            showMessage(result.message || "重新寄送失敗");
            return;
        }

        inputs.forEach(input => input.value = "");
        inputs[0].focus();

        showMessage("新的驗證碼已寄送至你的電子郵件信箱", true);
        startCooldown(60);

    } catch (error) {
        showMessage("網路連線異常，請稍後再試");
    } finally {
        if (!cooldownInterval) {
            resendBtn.disabled = false;
        }
    }
}

verifyBtn.addEventListener("click", verifyEmail);
resendBtn.addEventListener("click", resendVerification);

if (email) {
    inputs[0].focus();
} else {
    showMessage("缺少 Email 資訊，請返回註冊頁面");
}
