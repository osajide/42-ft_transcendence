const errors = document.getElementById("errorCont");
const baseUrl = window.location.host;
const background = document.getElementById("backg");
const loader = document.getElementById("loader");
let notiSocket;
let glob_endp = window.location.origin.split(":");
glob_endp = glob_endp[0] + ":" + glob_endp[1] + ":8000";

let user_data;

const removeElement = (e) => {
  if (e.classList.contains("game")) {
    updateUrl("games", "push", "");
    let timer = setInterval(() => {
      if (startGame) {
        startGame(e.id.split("_")[1]);
        clearInterval(timer);
      }
    }, 10);
  }
  e.remove();
};

const raiseWarn = (msg, type = "error") => {
  // //console.log(msg)
  raiseWarn.timers = [];
  errors.innerHTML += components.warning(msg, type);
  let self = document.getElementsByClassName("warn");
  self = self[self.length - 1];
  if (msg == "Session expired" || msg == "Invalid Token" || msg == "User not found") {
    logout();
    return "Error";
  }
  let s = setInterval(() => {
    // self.remove();
    if (!errors.lastElementChild) return clearTimeout(s);
    errors.lastElementChild.remove();
  }, 3000);
  if (type == "error") return "Error";
};

const fetchWithToken = async (
  url,
  endpoint,
  method,
  body = null,
  recursive = 0
) => {
  let data = "Error";
  if (endpoint != "/register/") {
    loader.classList.add("show");
    loader.classList.remove("hide");
  }
  settings = {
    method: method,
    credentials: "include",
  };
  // if (body && body instanceof FormData && body.has('avatar')) {
  settings.body = body;
  // } else if (body) settings.body = JSON.stringify(body);
  // //console.log(body)
  const response = await fetch(url.split(':')[0] + '://' + window.location.hostname + '/api' + endpoint, settings);
  loader.classList.add("hide");
  loader.classList.remove("show");

  if (response.ok) data = await response.json();
  //console.log(data)
  // //console.log(data, endpoint, data.error);
  if (response.status === 401) {
    if (!recursive) {
      const refreshResponse = await fetch(`${url.split(':')[0] + '://' + window.location.hostname + '/api'}/api/refresh/`, {
        method: "POST",
        credentials: "include",
      });
      if (refreshResponse.ok)
        return await fetchWithToken(url, endpoint, method, body, 1);
      data = await response.json();
    }
  }
  if (data.error) {
    return raiseWarn(data.error);
  } else if (data.email && !response.ok) {
    return raiseWarn(data.email);
  }

  if (
    endpoint != "/register/" &&
    endpoint != "/login/" &&
    endpoint != "/verify_code/" &&
    endpoint != "/setup_twofa/" &&
    data == "Error"
  ) {
    return raiseWarn("Session expired");
  }
  return data;
};
/******************** Globales ********************/

const icons = {
  profile: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M480-480q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47ZM160-160v-112q0-34 17.5-62.5T224-378q62-31 126-46.5T480-440q66 0 130 15.5T736-378q29 15 46.5 43.5T800-272v112H160Zm80-80h480v-32q0-11-5.5-20T700-306q-54-27-109-40.5T480-360q-56 0-111 13.5T260-306q-9 5-14.5 14t-5.5 20v32Zm240-320q33 0 56.5-23.5T560-640q0-33-23.5-56.5T480-720q-33 0-56.5 23.5T400-640q0 33 23.5 56.5T480-560Zm0-80Zm0 400Z"/></svg>`,
  chats: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M880-80 720-240H320q-33 0-56.5-23.5T240-320v-40h440q33 0 56.5-23.5T760-440v-280h40q33 0 56.5 23.5T880-640v560ZM160-473l47-47h393v-280H160v327ZM80-280v-520q0-33 23.5-56.5T160-880h440q33 0 56.5 23.5T680-800v280q0 33-23.5 56.5T600-440H240L80-280Zm80-240v-280 280Z"/></svg>`,
  friends: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM360-480q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47Zm400-160q0 66-47 113t-113 47q-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm240-320q33 0 56.5-23.5T440-640q0-33-23.5-56.5T360-720q-33 0-56.5 23.5T280-640q0 33 23.5 56.5T360-560Zm0 320Zm0-400Z"/></svg>`,
  games: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M189-160q-60 0-102.5-43T42-307q0-9 1-18t3-18l84-336q14-54 57-87.5t98-33.5h390q55 0 98 33.5t57 87.5l84 336q2 9 3.5 18.5T919-306q0 61-43.5 103.5T771-160q-42 0-78-22t-54-60l-28-58q-5-10-15-15t-21-5H385q-11 0-21 5t-15 15l-28 58q-18 38-54 60t-78 22Zm3-80q19 0 34.5-10t23.5-27l28-57q15-31 44-48.5t63-17.5h190q34 0 63 18t45 48l28 57q8 17 23.5 27t34.5 10q28 0 48-18.5t21-46.5q0 1-2-19l-84-335q-7-27-28-44t-49-17H285q-28 0-49.5 17T208-659l-84 335q-2 6-2 18 0 28 20.5 47t49.5 19Zm348-280q17 0 28.5-11.5T580-560q0-17-11.5-28.5T540-600q-17 0-28.5 11.5T500-560q0 17 11.5 28.5T540-520Zm80-80q17 0 28.5-11.5T660-640q0-17-11.5-28.5T620-680q-17 0-28.5 11.5T580-640q0 17 11.5 28.5T620-600Zm0 160q17 0 28.5-11.5T660-480q0-17-11.5-28.5T620-520q-17 0-28.5 11.5T580-480q0 17 11.5 28.5T620-440Zm80-80q17 0 28.5-11.5T740-560q0-17-11.5-28.5T700-600q-17 0-28.5 11.5T660-560q0 17 11.5 28.5T700-520Zm-360 60q13 0 21.5-8.5T370-490v-40h40q13 0 21.5-8.5T440-560q0-13-8.5-21.5T410-590h-40v-40q0-13-8.5-21.5T340-660q-13 0-21.5 8.5T310-630v40h-40q-13 0-21.5 8.5T240-560q0 13 8.5 21.5T270-530h40v40q0 13 8.5 21.5T340-460Zm140-20Z"/></svg>`,
  errorIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#db0000"><path d="M480-280q17 0 28.5-11.5T520-320q0-17-11.5-28.5T480-360q-17 0-28.5 11.5T440-320q0 17 11.5 28.5T480-280Zm-40-160h80v-240h-80v240Zm40 360q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>`,
  alertIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M280-420q25 0 42.5-17.5T340-480q0-25-17.5-42.5T280-540q-25 0-42.5 17.5T220-480q0 25 17.5 42.5T280-420Zm200 0q25 0 42.5-17.5T540-480q0-25-17.5-42.5T480-540q-25 0-42.5 17.5T420-480q0 25 17.5 42.5T480-420Zm200 0q25 0 42.5-17.5T740-480q0-25-17.5-42.5T680-540q-25 0-42.5 17.5T620-480q0 25 17.5 42.5T680-420ZM480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>`,
  notIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M160-200v-80h80v-280q0-83 50-147.5T420-792v-28q0-25 17.5-42.5T480-880q25 0 42.5 17.5T540-820v28q80 20 130 84.5T720-560v280h80v80H160Zm320-300Zm0 420q-33 0-56.5-23.5T400-160h160q0 33-23.5 56.5T480-80ZM320-280h320v-280q0-66-47-113t-113-47q-66 0-113 47t-47 113v280Z"/></svg>`,
  invitationIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M720-400v-120H600v-80h120v-120h80v120h120v80H800v120h-80Zm-360-80q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47ZM40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm80-80h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm240-320q33 0 56.5-23.5T440-640q0-33-23.5-56.5T360-720q-33 0-56.5 23.5T280-640q0 33 23.5 56.5T360-560Zm0-80Zm0 400Z"/></svg>`,
  messageIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M240-400h320v-80H240v80Zm0-120h480v-80H240v80Zm0-120h480v-4q-37-8-67.5-27.5T600-720H240v80ZM80-80v-720q0-33 23.5-56.5T160-880h404q-4 20-4 40t4 40H160v525l46-45h594v-324q23-5 43-13.5t37-22.5v360q0 33-23.5 56.5T800-240H240L80-80Zm80-720v480-480Zm600 80q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Z"/></svg>`,
  tournementIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M280-120v-80h160v-124q-49-11-87.5-41.5T296-442q-75-9-125.5-65.5T120-640v-40q0-33 23.5-56.5T200-760h80v-80h400v80h80q33 0 56.5 23.5T840-680v40q0 76-50.5 132.5T664-442q-18 46-56.5 76.5T520-324v124h160v80H280Zm0-408v-152h-80v40q0 38 22 68.5t58 43.5Zm200 128q50 0 85-35t35-85v-240H360v240q0 50 35 85t85 35Zm200-128q36-13 58-43.5t22-68.5v-40h-80v152Zm-200-52Z"/></svg>`,
  challengeIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" fill="#31dede" id="challenge" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M189-160q-60 0-102.5-43T42-307q0-9 1-18t3-18l84-336q14-54 57-87.5t98-33.5h390q55 0 98 33.5t57 87.5l84 336q2 9 3.5 18.5T919-306q0 61-43.5 103.5T771-160q-42 0-78-22t-54-60l-28-58q-5-10-15-15t-21-5H385q-11 0-21 5t-15 15l-28 58q-18 38-54 60t-78 22Zm3-80q19 0 34.5-10t23.5-27l28-57q15-31 44-48.5t63-17.5h190q34 0 63 18t45 48l28 57q8 17 23.5 27t34.5 10q28 0 48-18.5t21-46.5q0 1-2-19l-84-335q-7-27-28-44t-49-17H285q-28 0-49.5 17T208-659l-84 335q-2 6-2 18 0 28 20.5 47t49.5 19Zm348-280q17 0 28.5-11.5T580-560q0-17-11.5-28.5T540-600q-17 0-28.5 11.5T500-560q0 17 11.5 28.5T540-520Zm80-80q17 0 28.5-11.5T660-640q0-17-11.5-28.5T620-680q-17 0-28.5 11.5T580-640q0 17 11.5 28.5T620-600Zm0 160q17 0 28.5-11.5T660-480q0-17-11.5-28.5T620-520q-17 0-28.5 11.5T580-480q0 17 11.5 28.5T620-440Zm80-80q17 0 28.5-11.5T740-560q0-17-11.5-28.5T700-600q-17 0-28.5 11.5T660-560q0 17 11.5 28.5T700-520Zm-360 60q13 0 21.5-8.5T370-490v-40h40q13 0 21.5-8.5T440-560q0-13-8.5-21.5T410-590h-40v-40q0-13-8.5-21.5T340-660q-13 0-21.5 8.5T310-630v40h-40q-13 0-21.5 8.5T240-560q0 13 8.5 21.5T270-530h40v40q0 13 8.5 21.5T340-460Zm140-20Z"/></svg>`,
  logout: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h280v80H200v560h280v80H200Zm440-160-55-58 102-102H360v-80h327L585-622l55-58 200 200-200 200Z"/></svg>`,
  block: (id) => {
    return /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" id="block_${id}" onclick="network(this)" class="block" height="24px" viewBox="0 -960 960 960" width="24px" fill="#db0000"><path d="M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm240-120q33 0 56.5-23.5T560-360q0-33-23.5-56.5T480-440q-33 0-56.5 23.5T400-360q0 33 23.5 56.5T480-280ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z"/></svg>`;
  },
  unblock: (id) => {
    return /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" id="unblock_${id}" onclick="network(this)" class="block" height="24px" viewBox="0 -960 960 960" width="24px" fill="#db0000"><path d="M240-640h360v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85h-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640Zm0 480h480v-400H240v400Zm240-120q33 0 56.5-23.5T560-360q0-33-23.5-56.5T480-440q-33 0-56.5 23.5T400-360q0 33 23.5 56.5T480-280ZM240-160v-400 400Z"/></svg>`;
  },
  back: /* svg */ (id) => {
    return `<svg xmlns="http://www.w3.org/2000/svg" id="close" onclick="closeDiv(this,'${id}')" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M560-240 320-480l240-240 56 56-184 184 184 184-56 56Z"/></svg>`;
  },
};

window.addEventListener("resize", () => {
  if (window.innerWidth < 767) {
    const profile_img = document.querySelector(
      '[for="profile"]:not([tabindex="0"])'
    );
    if (profile_img) profile_img.setAttribute("for", "menu");
    const menuToggler = document.getElementById("menu");
    if (menuToggler?.checked) menuToggler.checked = 0;
  } else {
    const profile_img = document.querySelector('[for="menu"]');
    if (profile_img) profile_img.setAttribute("for", "profile");
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    const popupToggler = document.getElementById("list_toggler");
    const notToggler = document.getElementById("notToggler");
    const menuToggler = document.getElementById("menu");
    // const expansionToggler = document.getElementById('expansionToggler');
    if (popupToggler && popupToggler.checked) popupToggler.checked = false;
    if (menuToggler && menuToggler.checked) menuToggler.checked = false;
    if (notToggler && notToggler.checked) notToggler.checked = false;
    // if (expansionToggler && expansionToggler.checked)
    // expansionToggler.checked = false
  }
});

window.addEventListener("click", (e) => {
  const togglers = document.querySelectorAll(".togglers:checked");
  togglers.forEach((a) => {
    const searcher = document.getElementById("searchUser");
    if (a.id == "list_toggler" && searcher) searcher.focus();
    if (e.target.parentElement != a.parentElement && a.id != "list_toggler")
      a.checked = false;
  });
});

const network = async (e) => {
  const choices = {
    remove: "invite",
    cancel: "invite",
    decline: "invite",
    accept: "remove",
    invite: "cancel",
    block: "unblock",
    unblock: "block",
  };
  let value = e.tagName == "svg" ? e.id : e.value;
  resp = await fetchWithToken(glob_endp, `/friend/${value}`, "POST", {});
  if (resp == "Error") return;
  const old = value.split("_");
  const newVal = choices[old[0]];
  if (e.tagName == "svg") {
    let elId = e.id.split("_");
    let lock = document.querySelector(".controls");
    let id = lock.querySelector(".block");
    id.remove();
    const change = {};
    change[old[0]] = "";
    makeSocket.latest[0].send(JSON.stringify(change));
    lock.innerHTML += icons[choices[elId[0]]](elId[1]);
  } else {
    e.innerHTML = newVal;
    value = `${newVal}_${old[1]}`;
    if (old[0] == "decline" || old[0] == "accept" || old[0] == "remove") {
      const rem = e.previousElementSibling || e.nextElementSibling;
      rem.remove();
    }
    const userName = e.offsetParent.querySelector("h3").innerHTML.split(" ")[0];
    updateUrl("friends", "", userName + "myFriends" + value.split("_")[1]);
  }
};

/******************** Forms ********************/

async function authenticate(e) {
  e.preventDefault();
  errors.innerHTML = "";
  let endpoint = "/register/";
  let form = new FormData(e.target);
  if (e.target.childElementCount < 5) endpoint = "/login/";
  if (e.target.id == "otp") {
    endpoint = "/verify_code/";
    tmp = new FormData();
    let s = "";
    for ([key, value] of form.entries()) s += value;
    tmp.set("code", s);
    form = tmp;
  }
  e.target.reset();
  let data = await fetchWithToken(glob_endp, endpoint, "POST", form);
  if (data == "Error") return;

  if (endpoint == "/register/") {
    return updateUrl("login", "push");
  } else {
    e.target.classList.add("hide");
    e.target.nextElementSibling.classList.add("hide");
    e.target.previousElementSibling.classList.add("hide");
    if (data[0] == "scan_qr") {
      const qr = await fetchWithToken(glob_endp, "/setup_twofa/");
      e.target.insertAdjacentElement("beforebegin", components.qr(qr.qrcode));
    } else {
      const otp = components.otp();
      e.target.previousElementSibling.classList.remove("hide");
      e.target.previousElementSibling.outerHTML =
        "<h3>Please enter the code from your OTP app</h3>";
      e.target.insertAdjacentElement("beforebegin", otp);
      otp.firstElementChild.firstElementChild.focus();
    }
  }

  if (data.message == "successfully Logged") {
    user_data = data.user;
    localStorage.setItem("user_data", JSON.stringify(user_data));
    notiSocket = makeSocket("", notified);
    return updateUrl("friends", "push");
  }
}

function notified(e) {
  const notifier = document.getElementById("notifier");
  const notContainer = document.getElementById("notiList");
  const data = JSON.parse(e.data);
  //console.log(data);
  if (data.error) {
    return raiseWarn(data.error);
  } else if (data.game_id !== undefined) {
    startGame(data.game_id);
  } else if (data.tournament_id !== undefined) {
    playTournament(data.tournament_id);
  } else if (data.game_invite) {
    raiseWarn(data.game_invite, "game");
  } else {
    data.map((n) => {
      if (n != "game_id" && notContainer) {
        if (data.length > 1)
          notContainer.innerHTML += components.notification_elem(n);
        else
          notContainer.innerHTML =
            components.notification_elem(n) + notContainer.innerHTML;
      }
    });
  }
  if (data.length && notifier) notifier.classList.remove("hide");
}

function makeSocket(endpoint, socketMethod) {
  let ws = 'ws'
  let proto = glob_endp.split(':')[0].slice(-1)
  if (proto == 's')
    ws += 's'
  const socket = new WebSocket(`wss://${window.location.hostname}/ws/${endpoint}`);
  // const socket = new WebSocket(`wss://127.0.0.1/ws/${endpoint}`);
  if (endpoint) makeSocket.latest.push(socket);
  socket.onerror = (event) => {
    return raiseWarn('Something went wrong');
  };

  socket.onopen = function (event) {
    //console.log("WebSocket is open now.");
  };

  socket.onmessage = socketMethod;

  socket.onclose = function (event) {
    if (event.target.url.indexOf("tournament") > -1) {
      closeSockets();
      if (startGame.timer) {
        clearTimeout(startGame.timer);
        startGame.timer = undefined;
      }
      if (startGame.tournamentSocket) startGame.tournamentSocket = undefined;
      let wait = setTimeout(() => {
        tournamentInfo.wins = undefined;
        tournamentInfo.matches = undefined;
        clearTimeout(wait)
      }, 7000);
    } else if (event.target.url.indexOf("game") > -1) makeSocket.latest.pop();
    //console.log("WebSocket is closed now.");
  };
  return socket;
}

const handleForm = () => {
  let myForm = document.getElementById("my_form");

  if (user_data) return updateUrl("friends", "push");
  myForm.querySelector("input").focus();
  myForm.addEventListener("submit", authenticate);
};

/******************** Game ********************/
let window_width = window.innerWidth - 40;
let window_height = window.innerHeight - 130;

const components = {
  menu_item: (text) => {
    let name = text.toLowerCase();
    if (name != "logout")
      return /*html*/ `<label for="${name}" tabindex="0">${icons[name]}${text}</label>`;
    return /*html*/ `<button onclick="logout(event)" type="submit">${icons[name]}${text}</button>`;
  },
  header: function () {
    let header = document.createElement("header");
    header.classList.add('d-flex')
    header.innerHTML = /*html*/ `
			<label class="img_label" for="">
				<img id="logo" src="./assets/42.svg" alt="logo" />
			</label>
			<input class="hide togglers" type="checkbox" id="menu"/>
			<nav>
				${["profile", "Friends", "Chats", "Games", "logout"]
        .map((a) => {
          return this["menu_item"](a);
        })
        .join("\n")}
			</nav>
			<label class="img_label" for="menu" tabindex="1">
				<img id="user" src="./assets/avatars/${user_data.avatar ? user_data.avatar.replace("/", "") : "user.svg"
      }" alt="logo" />
			</label>
		`;
    return header;
  },
  card: (data, avatar) => {
    return /*html*/ `<div class="card ${data.result.toLowerCase()}">
    <div class="players">
    <img src="${"./assets/avatars/" + avatar.replace("/", "")}" alt="${user_data.first_name
      }"/>
      <span>VS</span>
      <img src="${"./assets/avatars/" + data.opponent_avatar.replace("/", "")
      }" alt="${user_data.first_name}"/>
      </div>
    <h4>${data.result}</h4>
    <p>Score: ${data.user_score > -1 ? data.user_score : 'LEFT'}</p>
    </div>`;
  },
  chat_banner: function (user) {
    return /* html */ `
    <div class="chatBanner">
    ${icons.back("friendChat")}
      <label class="friendData">
        <img src="${!user.avatar ? "assets/avatars/user.svg" : user.avatar
      }" alt="${user.name}"/>
        <h6>${user.name}</h6>
      </label>
      <div class="controls">
        ${icons.challengeIcon}
        ${icons.block(user.id)}
      </div>
    </div>
    `;
  },
  user_label: function (user, name, index) {
    if (name == "search_friends") name = "myFriends";
    return /* html */ `
			<input id="${user.first_name + name + user.id
      }" type="radio" class="chat_member hide" name="${name}" value="${user?.id
      }"/>
			<label onKeyDown="selction(event)" for="${user.first_name + name + user.id
      }" class="user_label ${(!index && name == "myFriends") || (name == "friendChat" && !user.seen)
        ? " bubble"
        : ""
      }" tabindex="0">
				<img src="${"./assets/avatars/" + user.avatar.replace("/", "")}" alt="${user.first_name
      }"/>
				<h4>${user.first_name} ${user.last_name}</h4>
			</label>
		`;
  },
  friends_list: function (usersList, name) {
    return /* html */ `
			<section id="${name + "_class"}" class="users_list">
				${usersList
        .map((users, index) => {
          return users
            .map((user) => {
              return this.user_label(user, name, index);
            })
            .join("\n");
        })
        .join("\n")}
			</section>
		`;
  },
  search: function () {
    return /* html */ `<input id="searchUser" type="text" placeholder="Type the user's name" autocomplete="off"/>
    ${this.friends_list([], "search_friends")}`;
  },
  popup: function (title, input_name) {
    let result = /* html */ `
      <section class="popup">
        <div class="list_title">
          <h2>${title}</h2>
          <label class="toggle_popup" for="list_toggler" tabindex="1">+</label>
        </div>`;
    if (title != "Add friends")
      result += /*html */ `
        ${components["friends_list"]([], input_name)}
      </section>`;
    else
      result += /*html */ `
      ${components["search"]()}
    </section>`;
    return result;
  },
  list: function (title, pop, input_name, users = [], add = null) {
    return /* html */ `
			<section class="list">
      <div  class="list_title">
			  <h2>${title}</h2>
        <input class="hide togglers" type="checkbox" id="list_toggler" class="togglers"/>
        <label class="toggle_popup" for="list_toggler" tabindex="0">+</label>
        ${components["popup"](pop, "friend")}
      </div>
			${components["friends_list"](users, input_name)}
			</section>
		`;
  },
  chat: function (user) {
    return /* html */ `
		<section id="chatCont">
      ${components.chat_banner(user)}
			<div id="chat">
			</div>
			<form id="messenger">
				<textarea id="msg" class="msg" name="msg" placeholder="Message..."></textarea>
				<input id="sub" type="submit" value="send" />
			</form>
			</section>`;
  },
  warning: function (msg, type) {
    if (type != "game")
      return /* html */ `
      <div onclick="removeElement(this)" class="warn ${type} d-flex" tabindex="0">${icons[type + "Icon"]
        }<p>${msg}</p></div>
    `;
    return /* html */ `
      <div onclick="removeElement(this)" id="game_${msg.game_id}" class="warn alert ${type}" tabindex="0">${icons.games}<p>${msg.description}</p></div>
    `;
  },
  profile: function (user = {}) {
    const choices = {
      accepted: ["block", "remove"],
      pending:
        user.last_action != user_data?.id ? ["accept", "decline"] : ["cancel"],
      "": ["invite"],
      blocked: [
        user.last_action != user_data?.id ? "block" : "unblock",
        "remove",
      ],
    };
    return /* html */ `
		<section id="userProfile">
    ${Object.keys(user).length
        ? /* html */ `
        <div class="userBanner">
        ${icons.back("myFriends")}
          <img src="${"./assets/avatars/" + user.avatar.replace("/", "")
        }" alt="${user.first_name}"/>
          <div class="userInfo">
          <h3>${user.first_name} ${user.last_name}</h3>
          <p>${user.email}</p>
          <small>${user.nickname}</small>
          <div class="relManager">
          ${choices[user.relationship]
          .map((action) => {
            return /* html */ `<button onclick="network(this)" class='button' value="${action}_${user.id}">${action}</button>`;
          })
          .join("\n")}
          </div>
        </div>
    </div>
    <div id="stats">
    ${components.cancel(user)}</div>`
        : ""
      }
    </section>`;
  },
  notification: function () {
    const not = document.createElement("section");
    const take_to = {
      invitation: "friends",
      "accept invitation": "friends",
      accept: "friends",
      chat: "chats",
    };

    not.setAttribute("id", "notification");
    not.addEventListener("click", async (e) => {
      const target = e.target;
      const notiCont = document.getElementById("notiList");
      // if (target.parentElement.tagName == "LABEL") {
      if (target.parentElement.id == "notiList" && target.tagName == "INPUT") {
        const to_go = target.id.split("_");
        let dest = `myFriends`;
        if (to_go[0] == "chat") dest = "friendChat";
        const push =
          window.location.pathname.replace("/", "") == take_to[to_go[0]]
            ? ""
            : "push";
        if (push.length) {
          updateUrl(take_to[to_go[0]], push, `${to_go[1]}${dest}${to_go[2]}`);
        } else {
          // The element is in the same page
          const targetInput = document.getElementById(
            `${to_go[1]}${dest}${to_go[2]}`
          );
          if (targetInput) {
            targetInput.checked = true;
            let ev = new Event("change", { bubbles: true });
            targetInput.dispatchEvent(ev);
          } else {
            if (to_go[0] == "chat") {
              const chatLabel = document.getElementById(
                `${to_go[1]}${dest}${to_go[2]}`
              );
              chatLabel.checked = true;
              chatLabel.dispatchEvent(new Event("change", { bubbles: true }));
            } else {
              await checkUser(to_go[2]);
            }
          }
        }
        notiSocket.send(JSON.stringify({ seen: +to_go[3] }));
        notiCont.querySelector(`[for="${target.id}"]`).remove();
        target.remove();
      }
      // }
      const notifier = document.getElementById("notifier");
      if (!notiCont.childElementCount && notifier)
        notifier.classList.add("hide");
    });

    not.innerHTML = /* html */ `
        <input id="notToggler" type="checkbox" class="hide togglers">
        <label for="notToggler" tabindex="0"><small id="notifier" class="notiBubble hide"></small>${icons["notIcon"]}</label>
        <div id="notiList" class="d-flex"></div>
    `;
    return not;
  },
  notification_elem: function (noti) {
    const myIcon =
      (noti.type != "invitation" ? "invitation" : "invitation") + "Icon";
    return /* html */ `
    <input type="radio" class="hide noti_member togglers" name="nots" id="${noti.type
      }_${noti.sender.first_name}_${noti.sender.id}_${noti.id}"/>
    <label for="${noti.type}_${noti.sender.first_name}_${noti.sender.id}_${noti.id
      }" class="notiLabel d-flex" tabindex="0">
      <img src="${"./assets/avatars/" + noti.sender.avatar.replace("/", "")
      }" alt="${noti.sender.first_name}"/>
      ${icons[myIcon]}
      <p>${noti.description}</p>
    </label>
  `;
  },
  qr: function (qr) {
    const container = document.createElement("div");
    container.id = "qrcode";
    container.innerHTML = /* html */ `
      <p>Please scan the QR code</p>
      <img src="${qr}" alt="qrcode"/>
      <label onclick="next(this)" id="next" class="button" tabindex="0">Next</label>
    `;
    return container;
  },
  otp: function () {
    const container = document.createElement("form");
    container.id = "otp";
    container.innerHTML = /* html */ `
      <div>
      <input type="text" maxlength="1" class="otpInput" name="digit1" required />
      <input type="text" maxlength="1" class="otpInput" name="digit2" required />
      <input type="text" maxlength="1" class="otpInput" name="digit3" required />
      <input type="text" maxlength="1" class="otpInput" name="digit4" required />
      <input type="text" maxlength="1" class="otpInput" name="digit5" required />
      <input type="text" maxlength="1" class="otpInput" name="digit6" required />
      </div>
      <label onclick="next(this)" id="reset" class="button" tabindex="0">Reset OTP</label>
    `;

    const otpInputs = container.querySelectorAll(".otpInput");
    otpInputs.forEach((input, index) => {
      input.addEventListener("input", (e) => {
        const value = e.target.value;
        // Only allow digits
        if (!Number.isInteger(+value)) {
          e.target.value = ""; // Clear invalid input
          return;
        }

        let i = index;
        // //console.log(otpInputs[i].value)
        while (i >= 0 && i - 1 > -1 && !otpInputs[i - 1].value.length) {
          otpInputs[i].value = "";
          i--;
        }
        if (i > -1) {
          otpInputs[i].focus();
          otpInputs[i].value = value;
        }

        // Move to the next input if not the last
        if (i < otpInputs.length - 1 && value) {
          otpInputs[i + 1].focus();
        }

        // Move to the previous input if it's empty
        // Automatically submit if all inputs are filled
        if (i === otpInputs.length - 1) {
          container.dispatchEvent(
            new Event("submit", { bubbles: true, cancelable: true })
          );
          otpInputs[0].focus();
        }
      });

      // Allow Backspace to focus previous input
      input.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && !input.value && index > 0) {
          otpInputs[index - 1].focus();
        }
      });
    });
    container.addEventListener("submit", authenticate);
    return container;
  },
  edit: function (data) {
    const container = document.createElement("form");
    container.setAttribute("id", "updateProfile");
    container.classList.add("auth_form");
    container.innerHTML = /* html */ `
      <label class="form_inp">
        Avatar:
        <input type="file" id="new_avatar" placeholder="test" name="avatar" accept="image/png, image/jpeg, image/svg, image/jpg" />
      </label>
      <label class="form_inp">
        First name:
        <input name="first_name" type="text" placeholder="Laarbi"/>
      </label>
      <label class="form_inp">
        Last name:
        <input name="last_name" type="text" placeholder="Treize"/>
      </label>
      <label class="form_inp">
        Username:
        <input name="nickname" type="text" placeholder="L337"/>
      </label>
      <input class="button" type="submit" value="Update profile"/>
            `;
    container.addEventListener("submit", async (e) => {
      e.preventDefault();
      const form = new FormData(e.target);
      const formData = new FormData();
      let count = 0;

      for (let [key, value] of form.entries()) {
        if (value.length && typeof value === "string") {
          formData.append(key, value);
          count++;
        } else if (typeof value === "object" && value.size) {
          const fileInput = document.getElementById("new_avatar");
          if (fileInput.files.length > 0) {
            formData.append("avatar", fileInput.files[0]);
          }
          count++;
        }
      }
      if (count) {
        resp = await fetchWithToken(
          glob_endp,
          "/update_profile/",
          "PATCH",
          formData
        );
        if (resp == "Error") return;
        for ([key, value] of Object.entries(resp)) {
          user_data[key] = value;
        }
        localStorage.setItem("user_data", JSON.stringify(user_data));
        return updateUrl("profile");
      } else {
        raiseWarn("Nothing to update", "alert");
      }
    });
    return container;
  },
  cancel: function (data) {
    // return /* html */ `
    //   ${Object.entries(data).map(([key, value]) => {
    //     return `<h2>${key}</h2><p>${value}</p>`;
    //   }).join('\n')}
    // `;
    return /* html */ `
    <div id="game_insight">
      <div class="game_count">
        <h4>Total Score</h4>
        <h2>${data.total_score}</h2>
      </div>
      <div class="game_count">
        <h4>Total played games</h4>
        <h2>${data.total_solo_games + data.total_played_tournament}</h2>
      </div>
      <div class="game_count">
        <h4>Total wins</h4>
        <h2>${data.total_win_games + data.total_win_tournaments}</h2>
      </div>
      <div class="game_count">
        <h4>Total losses</h4>
        <h2>${data.total_loss_games + data.total_loss_tournaments}</h2>
      </div>
    </div>
    <div id="game_stats">
      <h3>Solo games</h3>
      <div class="graph">
      <span class="bar" data-insight="${(
        (data.total_win_games / (data.total_solo_games || 1)) * (!data.total_solo_games ? 0 : 1) *
        100
      ).toFixed(2)}%" data-count="${data.total_win_games
      }" style="width: calc(1px + ${data.total_win_games / (data.total_solo_games || 1)
 * (!data.total_solo_games ? 0 : 1)      } * 100%)"></span>
      <span class="bar" data-insight="${(
        (data.total_loss_games / (data.total_solo_games || 1)) * (!data.total_solo_games ? 0 : 1) *
        100
      ).toFixed(2)}%" data-count="${data.total_loss_games
      }" style="width: calc(1px + ${data.total_loss_games / (data.total_solo_games || 1)
 * (!data.total_solo_games ? 0 : 1)      } * 100%)"></span></div>
      <h3>Tournaments</h3>
      <div class="graph"><span class="bar" data-insight="${(
        (data.total_win_tournaments / (data.total_played_tournament || 1)) * (!data.total_played_tournament ? 0 : 1) *
        100
      ).toFixed(2)}%" data-count="${data.total_win_tournaments
      }" style="width: calc(1px + ${data.total_win_tournaments / (data.total_played_tournament || 1)
 * (!data.total_played_tournament ? 0 : 1)      } * 100%)"></span>
      <span class="bar" data-insight="${(
        (data.total_loss_tournaments / (data.total_played_tournament || 1)) * (!data.total_played_tournament ? 0 : 1) *
        100
      ).toFixed(2)}%" data-count="${data.total_loss_tournaments
      }" style="width: calc(1px + ${data.total_loss_tournaments / (data.total_played_tournament || 1)
 * (!data.total_played_tournament ? 0 : 1)      } * 100%)"></span></div>
    </div>
    <h3>Game history</h3>
    <div id="recent_games">
      ${data.recent_games
        .map((d) => {
          return components.card(d, data.avatar);
        })
        .join("\n")}
    </div>
  `;
  },
};

async function next(e) {
  if (e.id == "next") {
    const qr = document.getElementById("qrcode");
    const otp = components.otp();
    qr.previousElementSibling.classList.remove("hide");
    qr.insertAdjacentElement("beforebegin", otp);
    otp.previousElementSibling.outerHTML =
      "<h3>Please enter the code from your OTP app</h3>";
    qr.remove();
    otp.firstElementChild.firstElementChild.focus();
  } else {
    const data = await fetchWithToken(glob_endp, "/setup_twofa/", "GET");
    if (data == "Error") return;
    const otp = document.getElementById("otp");
    const qr = components.qr(data.qrcode);
    otp.previousElementSibling.classList.add("hide");
    otp.insertAdjacentElement("beforebegin", qr);
    // otp.previousElementSibling.outerHTML =
    //   "<h3>Please enter the code from your OTP app</h3>";
    otp.remove();
  }
}

async function checkUser(endpoint) {
  const updateCont = document.getElementById("userProfile");
  response = await fetchWithToken(
    glob_endp,
    `${"/friend/profile/"}${endpoint}/`
  );
  if (response == "Error") return;
  updateCont.innerHTML = components["profile"](response)
    .trim()
    .split("\n")
    .slice(1, -1)
    .join("\n");
}

function logout(e) {
  if (e) {
    e.preventDefault();
    fetchWithToken(glob_endp, '/logout/');
  }
  localStorage.removeItem("user_data");
  user_data = undefined;
  if (notiSocket) notiSocket.close();
  closeSockets();
  notiSocket = undefined;
  updateUrl("login", "push");
}

function selction(e) {
  if (e.key == "Enter") {
    e.srcElement.control.checked = true;
    e.srcElement.control.dispatchEvent(new Event("change", { bubbles: true }));
  }
}

function closeDiv(e, name) {
  const target = document.querySelector(`[name="${name}"]:checked`);
  if (target) {
    target.checked = false;
    target.dispatchEvent(new Event("change", { bubbles: true }));
    document.querySelector(".expand").classList.remove("expand");
    closeSockets();
  }
}

const pages = {
  "/": {
    data: /*html*/ `
			<section id="page" class="d-flex">
			<label class="img_label" for="/">
				<img id="logo" src="./assets/42.svg" alt="logo" />
			</label>
		<section>
			<h1>JOIN - CHAT - PLAY</h1>
			<p>Join us - Chat with your friends - Play!</p>
		</section>
		<section class="indent d-flex">
			<label for="signin" class="button">Sign in</label>
			<label for="loginin" class="button">Login</label>
			<span></span>
			<label for="" class="button" onclick="auth42()">Continue with 42</label>
		</section>

			</section>
		`,
    id: "landing_page",
    func: () => { },
    glob: false,
  },
  login: {
    data: /*html */ `
			<section id="page">
		
			<label class="img_label" for="/">
				<img id="logo" src="./assets/42.svg" alt="logo" />
			</label>
		<h2>Welcome back!</h2>
		<form id="my_form" class="auth_form">
			<label class="form_inp">
				Email:
				<input name="email" type="email" placeholder="example@example.com" autocomplete="email" required/>
        <small>Required</small>
			</label>
			<label class="passwd form_inp">
				Password:
				<input name="password" type="password" placeholder="********" autocomplete="current-password" required/>
        <small>Required</small>
			</label>
			<input class="button" type="submit" value="Login"/>
		</form>
		<small>Don't have an account? <label class="inline_label" for="signin">Join</label> us today!</small>

			</section>
		`,
    id: "login_page",
    func: handleForm,
    glob: false,
  },
  signin: {
    data: /*html */ `
			<section id="page">
		
			<label class="img_label" for="/">
				<img id="logo" src="./assets/42.svg" alt="logo" />
			</label>
		<h2>Join us!</h2>
		<form id="my_form" class="auth_form">
			<div>
				<label class="form_inp">
					First name:
					<input name="first_name" type="text" placeholder="Laarbi" required/>
        <small>Required</small>
          </label>
				<label class="form_inp">
					Last name:
					<input name="last_name" type="text" placeholder="Treize" required/>
        <small>Required</small>
          </label>
			</div>
			<label class="form_inp">
				Email:
				<input name="email" type="email" placeholder="example@example.com" autocomplete="email" required/>
        <small>Required</small>
        </label>
			<label class="passwd form_inp">
				Password:
				<input name="password" type="password" placeholder="********" autocomplete="new-password" required/>
        <small>Required</small>
        </label>
			<label class="passwd form_inp">
				Confirm password:
				<input name="confirm_password" type="password" placeholder="********" autocomplete="disabled" required/>
        <small>Required</small>
        </label>
			<input class="button" type="submit" value="Sign in"/>
		</form>
		<small>Already a member? Go to <label class="inline_label" for="loginin">Login</label>!</small>

			</section>
		`,
    id: "signin_page",
    func: handleForm,
    glob: false,
  },
  profile: {
    data: /*html*/ `
			<section id="page">
        <div id="updatable" class="list">
          <img id="user_avatar" src="./assets/avatars/user.svg" alt="" />
          <h3 id="user_name">L3arbi 1337</h3>
          <p id="user_email">l3arbi.1337.ma</p>
          <h5 id="user_nickname">l337</h5>
        </div>
        <div id="stats">
        </div>
			</section>
		`,
    id: "profile",
    func: async () => {
      const update = document.getElementById("stats");
      const data = await fetchWithToken(glob_endp, `/profile/`, "GET");
      if (data == "Error") return;
      document.getElementById("updatable").innerHTML = fillProfile(data);
      document.getElementById("modeSwitch").addEventListener("click", (e) => {
        const choices = {
          Edit: "Cancel",
          Cancel: "Edit",
        };
        const choice = e.target.innerHTML;
        e.target.innerHTML = choices[choice];
        if (choice == "Cancel")
          return (update.innerHTML = components[choice.toLowerCase()](data));
        update.innerHTML = "<h2>Edit your profile</h2>";
        update.appendChild(components[choice.toLowerCase()](data));
      });
      document.getElementById("colorPicker").addEventListener("input", (e) => {
        localStorage.setItem("my_color", e.target.value);
      });
      update.innerHTML = components["cancel"](data);
    },
    glob: true,
  },
  chats: {
    data: /*html*/ `
			<section id="page">
				${components["list"]("Chats", "Start conversation", "friendChat", [])}
				<section id="chatCont"></section>
			</section>
		`,
    id: "chats",
    func: chatroom,
    glob: true,
  },
  games: {
    data: /* html */ `
  		<section id="page" class="lobby">
        <div class='hide' id="game_mode_nav">
          <input type="radio" id="games_home" value="" name="game_mode" checked/>
          <input type="radio" id="vs" value="solo" name="game_mode" />
          <input type="radio" id="jn_tour" value="tournament" name="game_mode" />
        </div>
        <section id="game_page">
          <div class="game_mode">
            <label class="button" for="vs">1 VS 1</label>
          </div>
          <div class="game_mode">
            <label class="button" for="jn_tour">Tournament</label>
          </div>
        </section>
        </section>
  	`,
    id: "games",
    func: lobby,
    glob: true,
  },
  friends: {
    data: /* html */ `
  		<section id="page">
        ${components.list("Friends", "Add friends", "myFriends")}
				${components["profile"]()}
  		</section>
  	`,
    id: "friends",
    func: friendsRoom,
    glob: true,
  },
};

function fillProfile(data) {
  const color = localStorage.getItem("my_color");
  if (!color) localStorage.setItem("my_color", "#31dede");
  return /* html */ `
  <img id="user_avatar" src="assets/avatars/${data.avatar.replace(
    "/",
    ""
  )}" alt="${data.first_name}" />
  <h3 id="user_name">${data.first_name} ${data.last_name}</h3>
  <p id="user_email">${data.email}</p>
  <h5 id="user_nickname">${data.nickname}</h5>
  <label for="colorPiker">Pick your paddle color: <input type="color" id="colorPicker" value="${color}"/></label>
  <button id="modeSwitch" class="button">Edit</button>`;
}

async function friendsRoom() {
  const friends = await fetchWithToken(glob_endp, `/friend/list/`, "GET");
  if (friends == "Error") return;
  document.querySelector(".list").outerHTML = components.list(
    "Friends",
    "Add friends",
    "myFriends",
    friends
  );
  search();
  const profileSection = document.getElementById("userProfile");
  listen("myFriends_class", profileSection, "/friend/profile/", "profile");
  listen("search_friends_class", profileSection, "/friend/profile/", "profile");
}

function lobby() {
  if (user_data === undefined) return updateUrl("login", "push");
  document.getElementById("game_mode_nav").addEventListener("change", (e) => {
    game_choice(e.target.value);
  });
}

async function chatroom() {
  const chats = await fetchWithToken(glob_endp, `/chats/list/`, "GET");
  const newchats = await fetchWithToken(glob_endp, `/chats/new/`, "GET");
  if (chats == "Error" || chats == "Error") return;
  document.querySelector(".list").outerHTML = components.list(
    "Chats",
    "Start conversation",
    "friendChat",
    chats
  );
  document.querySelector("#friend_class").outerHTML = components[
    "friends_list"
  ](newchats, "friend");
  const messages = document.getElementById("chatCont");
  listen("friendChat_class", messages, "", "chat");
  listen("friend_class", messages, "/chats/new/", "chat");
}

function listen(id, change, endpoint, compo) {
  document.querySelector("#" + id).addEventListener("change", async (e) => {
    if (e.target.checked) {
      if (e.target.nextElementSibling.classList.contains("bubble"))
        e.target.nextElementSibling.classList.remove("bubble");
      let data;
      if (compo == "profile") {
        response = await fetchWithToken(
          glob_endp,
          `${endpoint}${e.target.value}/`
        );
        if (response == "Error") return;
        data = response;
        // response.user = response;
        // data = response;
      } else {
        data = {
          avatar: e.target.nextElementSibling.firstElementChild.src,
          name: e.target.nextElementSibling.lastElementChild.innerHTML,
          id: e.target.value,
        };
      }
      change.classList.add("expand");
      change.innerHTML = components[compo](data)
        .trim()
        .split("\n")
        .slice(1, -1)
        .join("\n");
      if (compo == "chat") {
        messenger("chats/" + e.target.value);
        document.querySelector(".chatBanner").addEventListener("click", (e) => {
          if (
            e.target.classList.contains("friendData") ||
            e.target.parentElement.classList.contains("friendData")
          ) {
            updateUrl(
              "friends",
              "push",
              data.name.split(" ")[0] + "myFriends" + data.id
            );
          } else if (
            e.target.id == "challenge" ||
            e.target.parentElement.id == "challenge"
          ) {
            let element =
              e.target.id == "challenge" ? e.target : e.target.parentElement;
            notiSocket.send(
              JSON.stringify({
                challenge: +element.nextElementSibling.id.split("_")[1],
              })
            );
            updateUrl("games", "push", "");
          }
        });
      }
      document.getElementById("list_toggler").checked = false;
    }
  });
}

const makeScriptElement = (tag, attributes) => {
  const element = document.createElement(tag);
  attributes.map((att) => {
    element.setAttribute(att[0], att[1]);
  });
  return element;
};

const loadResources = (path) => {
  let styleFile = document.querySelector("#pageStyle");
  let scriptFile = document.querySelector("#pageScript");
  let file = path;
  if (scriptFile) scriptFile.remove();
  if (["login", "signin", "/"].indexOf(path) > -1) file = "auth";
  styleFile.setAttribute("href", `./styles/${file}.css`);
  scriptFile = makeScriptElement("script", [
    ["id", "pageScript"],
    ["src", `./scripts/${file}.js`],
  ]);
  document.body.appendChild(scriptFile);
  scriptFile.onload = () => {
    pages[path].func(["login, signin"].includes(path) ? null : "chat");
  };
};

function closeSockets() {
  while (makeSocket.latest.length) {
    try {
      makeSocket.latest[makeSocket.latest.length - 1].close();
    } catch (e) { }
    makeSocket.latest.pop();
  }
}

const updateUrl = (path = "/", mode = "", targetId = "") => {
  const app = document.getElementById("landing");
  const main = document.getElementsByTagName("main")[0];
  const myForm = document.getElementById("messenger");
  closeSockets();

  if (path != "/" && path[0] == "/") path = path.replace("/", "");
  let id = path;
  if (path == "login") id = "loginin";
  else if (path == "index.html") {
    window.history.replaceState(null, null, "/");
    path = "/";
    return;
  }
  if (!pages[path]) {
    path = "/";
    id = "/";
    window.history.replaceState(null, null, "/");
  }
  let currentUrl = window.location.href;
  loadResources(path);
  currentUrl = new URL(currentUrl);
  currentUrl.pathname = path;
  if (mode == "push") window.history.pushState({}, "", currentUrl);
  document.getElementById(id).checked = true;
  main.id = pages[path].id;
  main.innerHTML = pages[path].data;

  if (pages[path].glob && app.childElementCount < 3) {
    let header = components["header"]();
    app.appendChild(header);
    app.appendChild(components["notification"]());
    background.classList.add("myblur");
    if (window.innerWidth >= 767) {
      const profile_img = header.querySelector('[for="menu"]');
      profile_img.setAttribute("for", "profile");
    }
  } else if (!pages[path].glob && app.childElementCount > 2) {
    document.getElementsByTagName("header")[0]?.remove();
    document.getElementById("notification")?.remove();
    background.classList.remove("myblur");
  }
  document.querySelector(`.select`)?.classList.remove("select");
  app.querySelector(`[for="${id}"`)?.classList.add("select");
  if (targetId.length) {
    let i = 0;
    let timer = setInterval(async () => {
      const target = main.querySelector("#" + targetId);
      i++;
      if (target && i < 10) {
        target.checked = true;
        target.dispatchEvent(new Event("change", { bubbles: true }));
        clearInterval(timer);
      } else if (i > 10) {
        if (targetId.indexOf("myFriends") > -1) {
          clearInterval(timer);
          await checkUser(targetId.split("myFriends")[1]);
        } else i = 0;
      }
    }, 10);
  }
  loader.classList.add("hide");
  loader.classList.remove("show");
};

loader.classList.add("show");
loader.classList.remove("hide");

document.body.onload = () => {
  makeSocket.latest = [];
  user_data = JSON.parse(localStorage.getItem("user_data"));
  const params = new URLSearchParams(window.location.search)
  if (params.size != 0) {
    user_data = JSON.parse(Object.fromEntries(params.entries()).data)
    reff = ["id", "first_name", "last_name", "email", "avatar", "user_state", "nickname"]
    if (JSON.stringify(Object.keys(user_data)) !== JSON.stringify(reff))
      user_data = undefined
    else
      localStorage.setItem("user_data", JSON.stringify(user_data));
  }
  let path = window.location.pathname.replace("/", "");
  if (!path.length) path = "/";
  if (params.size != 0 && user_data) {
    currentUrl = new URL(window.location.origin);
    currentUrl.pathname = path;
    window.history.pushState({}, "", currentUrl);
  }
  if (!user_data && ["login", "signin", "/"].indexOf(path) < 0) {
    raiseWarn("Session expired");
    return updateUrl("login", "push");
  } else if (["login", "signin", "/"].indexOf(path) < 0)
    notiSocket = makeSocket("", notified);
  else if (user_data) {
    return updateUrl("friends", "push");
  }
  return updateUrl(path);
};

document.getElementById("spa_nav").addEventListener("change", (e) => {
  updateUrl(e.target.value, "push");
});

window.addEventListener("popstate", (e) => {
  const path = window.location.href.split(baseUrl)[1];
  updateUrl(path, "pop");
});

window.addEventListener("pushstate", (e) => {
  const path = window.location.href.split(baseUrl)[1];
  updateUrl(path);
});
