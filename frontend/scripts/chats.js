function receiveMessage(event) {
  const messenger = document.getElementById("chat");
  const data = JSON.parse(event.data);
  if (data.history) {
    let lock = document.querySelector(".controls");
    if (data.status == "blocked" && data.last_action_by == user_data.id) {
      let id = lock.querySelector(".block").id;
      lock.querySelector(".block").remove();
      lock.innerHTML += icons.unblock(id.split("_")[1]);
    } else if (data.status == "blocked")
      lock.querySelector(".block").removeAttribute("onclick");
    const separator = '<span class="newMsgs"></span>';
    data.history.map((oldMsgs, index) => {
      oldMsgs.map((oldMsg) => {
        tmp = messenger.innerHTML
          .replace("animateF", "")
          .replace("animate", "");
        messenger.innerHTML =
          tmp +
          `<p class="message ${oldMsg.owner == user_data.id ? "myMsg" : "friend"
          } animateF">${oldMsg.content}</p>`;
        messenger.scrollTop = messenger.scrollHeight;
      });
      if (!index && data.history[1].length > 0)
        messenger.innerHTML += separator;
    });
    let timer = setTimeout(() => {
      messenger.scrollTop = messenger.scrollHeight;
      clearTimeout(timer)
    }, 20);
  } else if (data.message) {
    if (messenger.querySelector(".newMsgs"))
      messenger.querySelector(".newMsgs").remove();
    tmp = messenger.innerHTML.replace("animateF", "").replace("animate", "");
    messenger.innerHTML =
      tmp + `<p class="message friend animateF">${data.message}</p>`;
    messenger.scrollTop = messenger.scrollHeight;
  }
  else if (data.reject) {
    if (messenger.querySelector(".newMsgs"))
      messenger.querySelector(".newMsgs").remove();
    tmp = messenger.innerHTML.replace("animateF", "").replace("animate", "");
    messenger.innerHTML =
      tmp + `<p class="message friend reject animateF">${data.reject}</p>`;
    messenger.scrollTop = messenger.scrollHeight;
  } else if (data.game_id !== undefined) {
    startGame(data.game_id);
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
  closeSockets()

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
  myForm.querySelector("#msg").focus();
  myForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(e, socket);
  });
}
