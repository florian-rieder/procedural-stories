var client_id = Date.now(); //uniqueId();
document.querySelector("#ws-id").textContent = client_id;

var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);

var markdown_converter = new showdown.Converter();

// Set the top margin to be equal to the header height so that the
// messages are not covered by the header
const header = document.querySelector("header");
const sticky = header.offsetHeight;
document.querySelector('#messages').style.marginTop = sticky + 'px';


let messagesContainer = document.getElementById("messages-container");
let messages = document.getElementById("messages");
let lastMessage = null;
let currentMessage = "";
let userScrolledDuringMessage = false;

messages.addEventListener("scroll", () => {
    userScrolledDuringMessage = true;
});

// document.getElementById('send').addEventListener('click', (e) => {
//     e.preventDefault();
//     this.form.dispatchEvent(new Event('submit'));
//     sendMessage();
// });

document.getElementById('end-conversation').addEventListener('click', (e) => {
    e.preventDefault();
    endConversation();
});


ws.onmessage = function (event) {
    let data = parseJSONrecursively(event.data);

    if (data.sender === "bot") {
        addBotMessage(data);
    }
};

function parseJSONrecursively(blob) {
    // https://stackoverflow.com/a/67576746/10914628
    let parsed = JSON.parse(blob);
    if (typeof parsed === 'string') parsed = parseJSONrecursively(parsed);
    return parsed;
}

function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById("messageText");

    input_value = input.value.trim();

    if (input_value === "") return;

    ws.send(JSON.stringify({"type": "message", "value": input_value}));
    input.value = '';

    document.getElementById("end-conversation").disabled = false;

    enableForm(false);
    addHumanMessage({ message: input_value });

    // Create the next bot message in the DOM
    lastMessage = createMessageElement();
    currentMessage += "Jeu: ";
    lastMessage.innerHTML = currentMessage;

    // Add the cursor
    let cursorMarker = document.createElement('span');
    cursorMarker.classList.add('cursor-marker');
    // Symbol for a thicker vertical bar
    cursorMarker.innerHTML = '&#9612;'
    lastMessage.appendChild(cursorMarker);
}

function createMessageElement() {
    let messageElement = document.createElement("li");
    messageElement.classList.add('message');
    messages.appendChild(messageElement);
    return messageElement;
}

function addHumanMessage(messageData) {
    let message = createMessageElement();
    message.innerHTML = "Vous: " + messageData.message;

    // Scroll to the bottom only if the user hasn't scrolled recently
    if (!userScrolledDuringMessage) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight - messagesContainer.clientHeight;
    }
}

function addBotMessage(messageData) {
    // Start of message
    if (messageData.type === 'start') {
        userScrolledDuringMessage = false;
    }
    // End of message
    else if (messageData.type === 'end') {
        console.log(currentMessage, messageData)
        lastMessage.innerHTML = '';
        const html = markdown_converter.makeHtml(currentMessage);
        const fullMessage = create(html);

        lastMessage.appendChild(fullMessage);

        currentMessage = "";
        enableForm(true);
    }
    // Error
    else if (messageData.type == 'error') {
        let message = createMessageElement();
        message.classList.add('error-msg')
        message.innerHTML = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i> ' + messageData.message
        enableForm(true);
    }
    // Info
    else if (messageData.type == 'info') {
        let message = createMessageElement();
        message.classList.add('info-msg')
        message.innerHTML = '<i class="fa fa-info-circle" aria-hidden="true"></i> ' + messageData.message
        enableForm(true);
    }
    // Stream
    else if (messageData.type == 'stream') {
        lastMessage.innerHTML = ""; // reset message contents

        console.log(messageData.message);
        currentMessage += messageData.message;

        // Automatically close unclosed triple backticks during message display
        fixed_triple_backticks = currentMessage;
        if (hasUnclosedTripleBacktick(currentMessage)) {
            fixed_triple_backticks = currentMessage + '\n```'
        }
        const html = markdown_converter.makeHtml(fixed_triple_backticks);
        const fragment = create(html);

        lastMessage.appendChild(fragment);
        lastMessage.querySelector(':last-child').style.display = 'inline';

        let cursorMarker = document.createElement('span');
        cursorMarker.classList.add('cursor-marker');
        // Symbol for a thicker vertical bar
        cursorMarker.innerHTML = '&#9612;'
        lastMessage.appendChild(cursorMarker);
    }

    // Scroll to the bottom only if the user hasn't scrolled recently
    if (!userScrolledDuringMessage) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight - messagesContainer.clientHeight;
    }
}

function enableForm(value) {
    let input = document.getElementById("messageText");
    input.disabled = !value;
    input.focus();

    const sendButton = document.getElementById("send");
    sendButton.disabled = !value;
}

function hasUnclosedTripleBacktick(inputString) {
    // Use a regular expression to check for unclosed triple backticks
    const regex = /```/g;

    // Count the number of occurrences of triple backticks
    const count = (inputString.match(regex) || []).length;

    // Check if the count is odd, indicating an unclosed triple backtick
    return count % 2 !== 0;
}

function endConversation() {
    // Tell the server we want to end the conversation
    ws.send(JSON.stringify({"type": "end_conversation"}))

    // Delete messages display
    while (messages.lastChild) {
        messages.removeChild(messages.lastChild);
    }

    document.getElementById("send").disabled = true;
    document.getElementById("end-conversation").disabled = true;
}

/**
 * @summary Generates a (pseudo)unique ID (used for session identification)
 * by combining the current time and a random number translated to base 36.
 * @returns {string} pseudo-unique 32 character ID
 * @see https://stackoverflow.com/a/34168882/1549992
 */
function uniqueId() {
    // desired length of Id
    var idStrLen = 32;
    // always start with a letter -- base 36 makes for a nice shortcut
    var idStr = (Math.floor((Math.random() * 25)) + 10).toString(36) + "_";
    // add a timestamp in milliseconds (base 36 again) as the base
    idStr += (new Date()).getTime().toString(36) + "_";
    // similar to above, complete the Id using random, alphanumeric characters
    do {
        idStr += (Math.floor((Math.random() * 35))).toString(36);
    } while (idStr.length < idStrLen);

    return (idStr);
}


/**
 * Create a document fragment from an HTML string while replacing HTML entities within text content.
 * @param {string} htmlStr - The HTML string to create a document fragment from.
 * @returns {DocumentFragment} - The created document fragment.
 */
function create(htmlStr) {
    // Create a document fragment and a temporary div element
    var frag = document.createDocumentFragment(),
        temp = document.createElement('div');

    // Set the HTML content of the temporary div element
    temp.innerHTML = htmlStr;

    /**
     * Recursively traverse through nodes and replace HTML entities within text content.
     * @param {Node} node - The node to process.
     */
    function replaceEntities(node) {
        // If the node is a text node
        if (node.nodeType === 3) {
            // Replace HTML entities within the text content
            node.nodeValue = node.nodeValue.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
        }
        // If the node is an element node
        else if (node.nodeType === 1) {
            // Recursively process child nodes
            for (var i = 0; i < node.childNodes.length; i++) {
                replaceEntities(node.childNodes[i]);
            }
        }
    }

    // Call replaceEntities to replace HTML entities within text nodes
    replaceEntities(temp);

    // Append child nodes of the temporary div element to the document fragment
    while (temp.firstChild) {
        frag.appendChild(temp.firstChild);
    }

    // Return the created document fragment
    return frag;
}

