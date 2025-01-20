Page({
    data: {
        scrollTop: 0,
        isHintVisible: true,
        websocket: null,
        isFirstResponse: true,
        startBotFlag: true,
        inputMessage: '',
        messages: [],// 用于存储聊天消息
        candidateInputs: [
            '你能做什么？',
            '市盈率是什么？',
            '最新芯片行业利好消息！',
            '中芯国际最近股价走势',
            '寒武纪当前股价和市盈率？',
            '今日大盘情况？',
            '推荐几只芯片股',
            '创业板估值如何？',
            'A股有多少支破净的公司？',
            '从最近10年看创业板是低估的吗？',
            '工商银行估值偏高不？',
            '特朗普最近出台了什么针对中国的新政策吗？对A股什么影响？',
            '价值板块当前是低估值吗？',
            '近10年紫光国微估值走势'
        ]
    },

    onLoad: function () {
        this.connectToServer();
    },
    onInputChange(e) {
        this.setData({
            inputMessage: e.detail.value
        });
        console.log("input set to " + this.data.inputMessage);
    },
    connectToServer: function () {
        const self = this;
        this.data.websocket = wx.connectSocket({
            url: 'wss://x297509z09.goho.co', // 或其他 WebSocket 服务器地址
            success: function () {
                console.log('Connected to WebSocket server.');
                wx.showToast({
                    title: '服务器已连接',
                    icon: 'none'
                });
            },
            fail: function (error) {
                console.error('WebSocket connection failed:', error);
                wx.showToast({
                    title: 'WebSocket连接失败，请检查网络连接',
                    icon: 'none'
                });
            }
        });

        this.data.websocket.onMessage(function (message) {
            self.displayMessageBot(message.data, 'bot');
        });

        this.data.websocket.onClose(function () {
            console.log('Disconnected from WebSocket server.');
            wx.showToast({
                title: 'WebSocket连接已断开，请刷新页面重试',
                icon: 'none'
            });
        });

        this.data.websocket.onError(function (error) {
            console.error('WebSocket error:', error);
            wx.showToast({
                title: 'WebSocket发生错误，请检查网络连接或服务器状态',
                icon: 'none'
            });
        });
    },
    senndMsgByInput: function () {
        const message = this.data.inputMessage;
        console.log("sendingByInput: " + message);
        this.sendMessage(message);
    },
    sendMsgByExam: function (event) {
        const message = event.currentTarget.dataset.message;
        console.log("sendingByExam: " + message);
        this.sendMessage(message);
    },
    sendMessage: function (message) {
        if (this.data.isFirstResponse) {
            this.setData({
                isHintVisible: false
            });
        }
        this.data.websocket.send({
            data: message,
            success: function () {
                console.log('Message sent:', message);
            }
        });
        this.displayMessageUser(message, 'user');
        this.setData({
            inputMessage: ''
        });
    },

    displayMessageUser: function (message, type) {
        const messages = this.data.messages;
        this.setData({
            messages: [...this.data.messages, { type: 'user', content: message }]
        });

        this.scrollToBottom();
    },
    splitStringByKeyword: function (inputString, keyword) {
        let result = [];
        let tempStr = '';
        let isKeyword = false;

        for (let i = 0; i < inputString.length; i++) {
            let char = inputString[i];
            tempStr += char;

            if (tempStr === keyword) {
                result.push(tempStr);
                tempStr = '';
                isKeyword = true; // 标记下一个片段为非关键字
            } else if (isKeyword && tempStr.length > 0) {
                // 如果当前片段已经包含字符且上一个片段是关键字，则当前片段为非关键字
                result.push(tempStr);
                tempStr = '';
                isKeyword = false; // 重置标记
            } else if (!isKeyword && tempStr.includes(keyword)) {
                // 如果当前片段包含关键字但不是完全匹配，需要拆分
                let keywordIndex = tempStr.indexOf(keyword);
                result.push(tempStr.slice(0, keywordIndex)); // 添加非关键字部分
                result.push(tempStr.slice(keywordIndex, keywordIndex + keyword.length)); // 添加关键字部分
                tempStr = tempStr.slice(keywordIndex + keyword.length); // 剩余部分继续处理
                isKeyword = true; // 下一个片段从非关键字开始
            }
        }

        // 添加最后剩余的非关键字部分（如果有）
        if (tempStr.length > 0) {
            result.push(tempStr);
        }

        // 合并连续的非关键字片段
        let finalResult = [];
        let tempArray = [];
        for (let item of result) {
            if (item === keyword) {
                if (tempArray.length > 0) {
                    finalResult.push(...tempArray);
                    tempArray = [];
                }
                finalResult.push(item);
            } else {
                tempArray.push(item);
            }
        }
        if (tempArray.length > 0) {
            finalResult.push(tempArray.join(''));
        }

        return finalResult;
    },
    creatRichFromText: function (inputMsg) {
        let result = [
            {
                name: 'div',
                children: []
            }
        ];
        const key_word = '点击复制链接';
        const split_strs = this.splitStringByKeyword(inputMsg, key_word);
        console.log(split_strs)

        for (let i = 0; i < split_strs.length; i++) {
            console.log(split_strs[i]);
            if (split_strs[i].includes(key_word)) {
                result[0].children.push({
                    name: 'a',
                    attrs: {
                        class: 'link',
                    },
                    children: [
                        {
                            type: 'text',
                            text: split_strs[i]
                        }
                    ]
                })
            } else {
                result[0].children.push({
                    type: 'text',
                    text: split_strs[i],
                })
            }
        }
        console.log(result);
        return result;
    },
    handleButtonClick: function () {
        console.log('new session request ');
        wx.reLaunch({
            url: '/pages/index/index' // 替换为你的首页路径
        });
    },
    handleLinkTap(event) {
        console.log("handleLinkTap：" + event.target.id);
        const url = event.target.dataset.url;
        console.log(url);
        if (url.length > 0) {
            wx.setClipboardData({
                data: url[0],
                success: () => {
                    wx.showModal({
                        title: '提示',
                        content: '链接已复制到剪贴板，请在浏览器中打开',
                        showCancel: false,
                        success: () => {
                            // 可以选择在这里进行其他操作，比如跳转到某个页面或关闭弹窗
                        }
                    });
                }
            });
        }
        // 注意：微信小程序中直接打开外部链接是被限制的，需要用户手动复制链接到浏览器中打开
    },
    displayMessageBot: function (message, type) {
        let links;
        const messages = this.data.messages;
        const isImage = message.startsWith('data:image/');
        if (!isImage) {
            let tuple = this.processMessage(message);
            message = tuple[0];
            links = tuple[1];
        }

        if (message === "EOS") {
            this.data.startBotFlag = true;
        } else {
            if (this.data.startBotFlag) {
                // handle the Rich Text with Link
                let isRichText = false;
                if (message.includes('点击复制链接')) {
                    isRichText = true;
                    message = this.creatRichFromText(message);
                }

                this.setData({
                    messages: [...this.data.messages, { type: 'bot', content: message, isImage: isImage, isRichText: isRichText, url: links }]
                });
                this.data.startBotFlag = false;
            } else {
                console.log("rec: " + message);
                this.data.messages[this.data.messages.length - 1].content = message;
                this.setData({
                    messages: this.data.messages
                });
            }
        }

        this.scrollToBottom();
    },

    processMessage: function (message) {
        const links = [];
        if (message.includes('https://') || message.includes('http://')) {
            const linkRegex = /(https?:\/\/[^\s]+)/g;
            let match;
            while ((match = linkRegex.exec(message)) !== null) {
                links.push(match[0]);
            }

            message = message.replace(linkRegex, '点击复制链接\n');
            // message = message.replace(/\n/g, '<br/>');
        }

        return [message, links];
    },
    scrollToBottom: function () {
        const query = wx.createSelectorQuery()
        // 通过class选择器定位到scorll-view
        query.select('.chat-history').boundingClientRect(res => {
            this.setData({
                // 由于res.height效果不明显，所以乘以100系数，这个系数可以根据实际效果调整
                scrollTop: res.height * 100
            })
        })
        query.exec(res => { })
    },
}
);