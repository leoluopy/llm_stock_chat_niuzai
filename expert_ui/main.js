let websocket;
let isFirstResponse = true;
let startBotFlag = true;
let botPDivCnt = 0;
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const messagesDiv = document.getElementById('messages');


function sendMessage(message) {
    const candidateInputs = document.getElementById('candidate-inputs');
    if (isFirstResponse) {
        candidateInputs.style.display = 'none'; // 隐藏候选输入内容
        isFirstResponse = false;
    }
    websocket.send(message);
    displayMessageUser(message, 'user');
}

function displayMessageUser(message, type) {
    const pDiv = document.createElement('p')
    pDiv.className = 'text-wrapper-user'


    // messageDiv.textContent = message;
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`
    pDiv.textContent = message

    messageDiv.appendChild(pDiv)
    messagesDiv.appendChild(messageDiv);

    // 确保滚动条到底部
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function openLink(url) {
    window.open(url, '_blank');
}

function replaceABCWithBCD(str, links) {
    let result = str;
    i = 0
    while (result.includes('点击查看链接')) {
        link = links[i]
        result = result.replace('点击查看链接', `<span class="clickable-link" onclick="openLink('${link}')">点击打开链接</span>`);
        i++
        if (i >= links.length) {
            break
        }
    }
    return result;
}

function displayMessageBot(message, type) {
    // console.log("in:" + messagesDiv.scrollHeight)
    if (message.startsWith('data:image/png;base64,')) {
        const messageDiv = document.createElement('div');
        const img = document.createElement('img');
        img.src = message;
        img.className = "chat-image"
        messageDiv.appendChild(img)
        messagesDiv.appendChild(messageDiv)
    } else {
        if (message.includes('https') || message.includes('http')) {
            console.log('msg:', message)

            inputString = message
            // 提取链接的正则表达式
            const linkRegex = /(https?:\/\/[^\s\n]+)/g;

            // 提取所有链接
            let matches;
            const links = [];
            while ((matches = linkRegex.exec(inputString)) !== null) {
                links.push(matches[0]);
                console.log(matches[0])
            }
            console.log('matched len:', links.length)
            // 替换链接为'点击查看链接'
            message = message.replace(linkRegex, '点击查看链接\n');
            message = replaceABCWithBCD(message, links)
        }
        message = message.replace(/\n/g, '<br>');
        if (message === "EOS") {
            console.log('start new')
            startBotFlag = true
            botPDivCnt++
        } else {
            if (startBotFlag) {
                console.log('new bot msg')
                const messageDiv = document.createElement('div');
                const pDiv = document.createElement('p')
                pDiv.className = 'text-wrapper-bot'
                pDiv.id = `text-bot-${botPDivCnt}`
                pDiv.innerHTML = message
                messageDiv.className = `chat-message ${type}`
                messageDiv.appendChild(pDiv)
                messagesDiv.appendChild(messageDiv);
                startBotFlag = false
            } else {
                console.log('append bot msg')
                const pDiv = document.getElementById(`text-bot-${botPDivCnt}`)
                pDiv.innerHTML = message
            }
        }
    }
    // 确保滚动条到底部
    // console.log("after:" + messagesDiv.scrollHeight)
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

document.addEventListener('DOMContentLoaded', () => {

    function connectToServer() {
        websocket = new WebSocket('wss://x297509z09.goho.co'); // oray launch https link with local http
        // websocket = new WebSocket('ws://192.168.31.222:8765');

        websocket.onopen = () => {
            console.log('Connected to WebSocket server.');
        };

        websocket.onmessage = (event) => {
            const botResponse = event.data;
            displayMessageBot(botResponse, 'bot');
        };

        websocket.onclose = () => {
            console.log('Disconnected from WebSocket server.');
            alert('WebSocket连接已断开，请刷新页面重试。');
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            alert('WebSocket发生错误，请检查网络连接或服务器状态。');
        };
    }


    // 在页面加载时连接到服务器
    connectToServer();

    sendButton.addEventListener('click', () => {
        const userMessage = userInput.value.trim();

        if (userMessage) {
            // 发送用户消息到服务器
            sendMessage(userMessage)
            // 清空输入框
            userInput.value = '';
        }
    });

    // 可选：监听键盘事件以发送消息（例如按下Enter键）
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendButton.click();
        }
    });
});