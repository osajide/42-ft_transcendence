function receiveMessage(event) {
  const messenger = document.getElementById("chat");
  const data = JSON.parse(event.data);
  if (data.status) {
    alert("Can't establish connection: " + data.reason);
    return;
  } else if (data.history) {
    const lock = document.getElementById("block");
    if (data.status == "blocked" && data.last_action_by == user_data.id)
      lock = icons.unblock(lock.value.split("_")[1]);
    const separator = '<span class="newMsgs"></span>';
    data.history.map((oldMsgs, index) => {
      oldMsgs.map((oldMsg) => {
        tmp = messenger.innerHTML
          .replace("animateF", "")
          .replace("animate", "");
        messenger.innerHTML =
          tmp +
          `<p class="message ${
            oldMsg.owner == user_data.id ? "myMsg" : "friend"
          } animateF">${oldMsg.content}</p>`;
        messenger.scrollTop = messenger.scrollHeight;
      });
      if (!index && data.history[1].length > 0)
        messenger.innerHTML += separator;
    });
    let timer = setTimeout(() => {
      messenger.scrollTop = messenger.scrollHeight;
    }, 20);
  } else if (data.message) {
    if (messenger.querySelector(".newMsgs"))
      messenger.querySelector(".newMsgs").remove();
    tmp = messenger.innerHTML.replace("animateF", "").replace("animate", "");
    messenger.innerHTML =
      tmp + `<p class="message friend animateF">${data.message}</p>`;
    messenger.scrollTop = messenger.scrollHeight;
  }
}

function sendMessage(e, socket) {
  const messenger = document.getElementById("chat");
  const msg = document.getElementById("msg");

  if (msg.value) {
    tmp = messenger.innerHTML.replace("animate", "");
    messenger.innerHTML =
      tmp + `<p class="message myMsg animate">${msg.value}</p>`;
    if (messenger.querySelector(".newMsgs"))
      messenger.querySelector(".newMsgs").remove();
    socket.send(JSON.stringify({ message: `${msg.value}` }));
    msg.value = "";
    messenger.scrollTop = messenger.scrollHeight;
  }
  // messenger.innerHTML = messenger.innerHTML.replace('animateF', '').replace('animate', '')
}

function messenger(endpoint) {
  myForm = document.getElementById("messenger");
  if (makeSocket.latest) {
    makeSocket.latest.close();
    makeSocket.latest = undefined;
  }
  const socket = makeSocket(endpoint, receiveMessage);

  myForm.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      myForm.querySelector("#sub").focus();
      let timer = setTimeout(() => {
        myForm.querySelector("#msg").focus();
        clearTimeout(timer);
      }, 100);
    }
  });

  myForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(e, socket);
  });
}
