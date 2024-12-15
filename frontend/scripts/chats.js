function receiveMessage(event) {
  console.log(event);
  const messenger = document.getElementById("chat");
  const data = JSON.parse(event.data);
  if (data.status) {
    alert("Can't establish connection: " + data.reason);
    return;
  }
  tmp = messenger.innerHTML.replace("animateF", "").replace("animate", "");
  messenger.innerHTML =
    tmp + `<p class="message friend animateF">${data.message}</p>`;
  messenger.scrollTop = messenger.scrollHeight;
}

function sendMessage(e, socket) {
  const messenger = document.getElementById("chat");
  const msg = document.getElementById("msg");

  if (msg.value) {
    tmp = messenger.innerHTML.replace("animate", "");
    messenger.innerHTML =
      tmp + `<p class="message myMsg animate">${msg.value}</p>`;
    socket.send(JSON.stringify({ message: `${msg.value}` }));
    msg.value = "";
    messenger.scrollTop = messenger.scrollHeight;
  }
  // messenger.innerHTML = messenger.innerHTML.replace('animateF', '').replace('animate', '')
}

function messenger(endpoint) {
  myForm = document.getElementById("messenger");
  const socket = makeSocket(endpoint, receiveMessage);

  myForm.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      myForm.querySelector("#sub").focus();
      let timer = setTimeout(() => {
        myForm.querySelector("#msg").focus();
        clearTimeout(timer)
      }, 100);
    }
  });

  myForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(e, socket);
  });
}
