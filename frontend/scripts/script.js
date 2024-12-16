const errors = document.getElementById("errorCont");
const baseUrl = window.location.host;
const background = document.getElementById("backg");
const loader = document.getElementById("loader");
let notiSocket;
let glob_endp = window.location.origin.split(":");
glob_endp = glob_endp[0] + ":" + glob_endp[1] + ":8000";

let user_data;
//  = {
//   first_name: "Oussama",
//   last_name: "Sajide",
//   email: "oussamasajide4@gmail.com",
//   id: 2,
//   avatar: "user.svg",
// };

const removeElement = (e) => {
  e.remove();
};

const raiseWarn = (msg, type = "error") => {
  errors.innerHTML += components.warning(msg, type);
  let self = document.getElementsByClassName("warn");
  self = self[self.length - 1];
  user_data = undefined;
  if (type == "error") localStorage.removeItem("user_data");
  let s = setTimeout(() => {
    removeElement(self);
    clearTimeout(s);
  }, 3000);
};

const fetchWithToken = async (url, endpoint, method, body = null) => {
  let data = "Error";
  if (endpoint != "/api/register/") {
    loader.classList.add("show");
    loader.classList.remove("hide");
  }
  settings = {
    method: method,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  };
  if (body) settings.body = JSON.stringify(body);
  const response = await fetch(url + endpoint, settings);

  loader.classList.add("hide");
  loader.classList.remove("show");

  if (response.ok) data = await response.json();
  console.log(data, endpoint);
  // if (endpoint != "/api/register/" && response.status === 401) {
  //   const refreshResponse = await fetch(`${url}/api/refresh/`, {
  //     method: "POST",
  //     credentials: "include",
  //   });

  //   if (refreshResponse.ok) {
  //     const data = await refreshResponse.json();
  //     const accessToken = data.access_token;
  //     localStorage.setItem("accessToken", accessToken);
  //     options.headers.Authorization = `Bearer ${accessToken}`;
  //     return fetch(url + endpoint, options);
  //   }

  //   //   // throw new Error("Unable to refresh token");
  // }
  if (data.error) {
    raiseWarn(data.error);
  } else if (data.detail) {
    raiseWarn(data.detail);
  }

  if (
    endpoint != "/api/register/" &&
    endpoint != "/api/login/" &&
    data == "Error"
  ) {
    raiseWarn("User logged out");
    updateUrl("", "");
  }
  return data;
};
/******************** Globales ********************/

const icons = {
  chats: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M880-80 720-240H320q-33 0-56.5-23.5T240-320v-40h440q33 0 56.5-23.5T760-440v-280h40q33 0 56.5 23.5T880-640v560ZM160-473l47-47h393v-280H160v327ZM80-280v-520q0-33 23.5-56.5T160-880h440q33 0 56.5 23.5T680-800v280q0 33-23.5 56.5T600-440H240L80-280Zm80-240v-280 280Z"/></svg>`,
  friends: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM360-480q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47Zm400-160q0 66-47 113t-113 47q-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm240-320q33 0 56.5-23.5T440-640q0-33-23.5-56.5T360-720q-33 0-56.5 23.5T280-640q0 33 23.5 56.5T360-560Zm0 320Zm0-400Z"/></svg>`,
  games: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M189-160q-60 0-102.5-43T42-307q0-9 1-18t3-18l84-336q14-54 57-87.5t98-33.5h390q55 0 98 33.5t57 87.5l84 336q2 9 3.5 18.5T919-306q0 61-43.5 103.5T771-160q-42 0-78-22t-54-60l-28-58q-5-10-15-15t-21-5H385q-11 0-21 5t-15 15l-28 58q-18 38-54 60t-78 22Zm3-80q19 0 34.5-10t23.5-27l28-57q15-31 44-48.5t63-17.5h190q34 0 63 18t45 48l28 57q8 17 23.5 27t34.5 10q28 0 48-18.5t21-46.5q0 1-2-19l-84-335q-7-27-28-44t-49-17H285q-28 0-49.5 17T208-659l-84 335q-2 6-2 18 0 28 20.5 47t49.5 19Zm348-280q17 0 28.5-11.5T580-560q0-17-11.5-28.5T540-600q-17 0-28.5 11.5T500-560q0 17 11.5 28.5T540-520Zm80-80q17 0 28.5-11.5T660-640q0-17-11.5-28.5T620-680q-17 0-28.5 11.5T580-640q0 17 11.5 28.5T620-600Zm0 160q17 0 28.5-11.5T660-480q0-17-11.5-28.5T620-520q-17 0-28.5 11.5T580-480q0 17 11.5 28.5T620-440Zm80-80q17 0 28.5-11.5T740-560q0-17-11.5-28.5T700-600q-17 0-28.5 11.5T660-560q0 17 11.5 28.5T700-520Zm-360 60q13 0 21.5-8.5T370-490v-40h40q13 0 21.5-8.5T440-560q0-13-8.5-21.5T410-590h-40v-40q0-13-8.5-21.5T340-660q-13 0-21.5 8.5T310-630v40h-40q-13 0-21.5 8.5T240-560q0 13 8.5 21.5T270-530h40v40q0 13 8.5 21.5T340-460Zm140-20Z"/></svg>`,
  errorIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#db0000"><path d="M480-280q17 0 28.5-11.5T520-320q0-17-11.5-28.5T480-360q-17 0-28.5 11.5T440-320q0 17 11.5 28.5T480-280Zm-40-160h80v-240h-80v240Zm40 360q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>`,
  alertIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M280-420q25 0 42.5-17.5T340-480q0-25-17.5-42.5T280-540q-25 0-42.5 17.5T220-480q0 25 17.5 42.5T280-420Zm200 0q25 0 42.5-17.5T540-480q0-25-17.5-42.5T480-540q-25 0-42.5 17.5T420-480q0 25 17.5 42.5T480-420Zm200 0q25 0 42.5-17.5T740-480q0-25-17.5-42.5T680-540q-25 0-42.5 17.5T620-480q0 25 17.5 42.5T680-420ZM480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>`,
  notIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M160-200v-80h80v-280q0-83 50-147.5T420-792v-28q0-25 17.5-42.5T480-880q25 0 42.5 17.5T540-820v28q80 20 130 84.5T720-560v280h80v80H160Zm320-300Zm0 420q-33 0-56.5-23.5T400-160h160q0 33-23.5 56.5T480-80ZM320-280h320v-280q0-66-47-113t-113-47q-66 0-113 47t-47 113v280Z"/></svg>`,
  invitationIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M720-400v-120H600v-80h120v-120h80v120h120v80H800v120h-80Zm-360-80q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47ZM40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm80-80h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm240-320q33 0 56.5-23.5T440-640q0-33-23.5-56.5T360-720q-33 0-56.5 23.5T280-640q0 33 23.5 56.5T360-560Zm0-80Zm0 400Z"/></svg>`,
  messageIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M240-400h320v-80H240v80Zm0-120h480v-80H240v80Zm0-120h480v-4q-37-8-67.5-27.5T600-720H240v80ZM80-80v-720q0-33 23.5-56.5T160-880h404q-4 20-4 40t4 40H160v525l46-45h594v-324q23-5 43-13.5t37-22.5v360q0 33-23.5 56.5T800-240H240L80-80Zm80-720v480-480Zm600 80q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Z"/></svg>`,
  tournementIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M280-120v-80h160v-124q-49-11-87.5-41.5T296-442q-75-9-125.5-65.5T120-640v-40q0-33 23.5-56.5T200-760h80v-80h400v80h80q33 0 56.5 23.5T840-680v40q0 76-50.5 132.5T664-442q-18 46-56.5 76.5T520-324v124h160v80H280Zm0-408v-152h-80v40q0 38 22 68.5t58 43.5Zm200 128q50 0 85-35t35-85v-240H360v240q0 50 35 85t85 35Zm200-128q36-13 58-43.5t22-68.5v-40h-80v152Zm-200-52Z"/></svg>`,
  challengeIcon: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" id="challenge" height="24px" viewBox="0 -960 960 960" width="24px" fill="#00bcbc"><path d="M762-96 645-212l-88 88-28-28q-23-23-23-57t23-57l169-169q23-23 57-23t57 23l28 28-88 88 116 117q12 12 12 28t-12 28l-50 50q-12 12-28 12t-28-12Zm118-628L426-270l5 4q23 23 23 57t-23 57l-28 28-88-88L198-96q-12 12-28 12t-28-12l-50-50q-12-12-12-28t12-28l116-117-88-88 28-28q23-23 57-23t57 23l4 5 454-454h160v160ZM334-583l24-23 23-24-23 24-24 23Zm-56 57L80-724v-160h160l198 198-57 56-174-174h-47v47l174 174-56 57Zm92 199 430-430v-47h-47L323-374l47 47Zm0 0-24-23-23-24 23 24 24 23Z"/></svg>`,
  logout: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px"><path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h280v80H200v560h280v80H200Zm440-160-55-58 102-102H360v-80h327L585-622l55-58 200 200-200 200Z"/></svg>`,
  block: /* svg */ `<svg xmlns="http://www.w3.org/2000/svg" id="block" height="24px" viewBox="0 -960 960 960" width="24px" fill="#db0000"><path d="M480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q54 0 104-17.5t92-50.5L228-676q-33 42-50.5 92T160-480q0 134 93 227t227 93Zm252-124q33-42 50.5-92T800-480q0-134-93-227t-227-93q-54 0-104 17.5T284-732l448 448Z"/></svg>`,
  back: /* svg */ (id) => {
    return `<svg xmlns="http://www.w3.org/2000/svg" id="close" onclick="closeDiv(this,'${id}')" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f1f1f1"><path d="M560-240 320-480l240-240 56 56-184 184 184 184-56 56Z"/></svg>`;
  },
};

window.addEventListener("resize", () => {
  if (window.innerWidth < 768) {
    const menuToggler = document.getElementById("menu");
    if (menuToggler?.checked) menuToggler.checked = 0;
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

// let dumb_users = [
//   { first_name: "ykhayri", avatar: "user.svg" },
//   { first_name: "ykhayri", avatar: "user.svg" },
//   { first_name: "ykhayri", avatar: "user.svg" },
//   { first_name: "ykhayri", avatar: "user.svg" },
//   { first_name: "ykhayri", avatar: "user.svg" },
// ];

const network = async (e) => {
  const choices = {
    remove: "invite",
    cancel: "invite",
    decline: "invite",
    accept: "remove",
    invite: "cancel",
  };
  resp = await fetchWithToken(glob_endp, `/friend/${e.value}`, "POST", {});
  if (resp == "Error") return;
  const old = e.value.split("_");
  const newVal = choices[old[0]];
  e.innerHTML = newVal;
  e.value = `${newVal}_${old[1]}`;
  if (old[0] == "decline" || old[0] == "accept") {
    const rem = e.previousElementSibling || e.nextElementSibling;
    rem.remove();
  }
  const userName = e.offsetParent.querySelector("h3").innerHTML.split(" ")[0];
  updateUrl("friends", "", userName + "myFriends" + e.value.split("_")[1]);
};

/******************** Forms ********************/

async function authenticate(e) {
  errors.innerHTML = "";
  let endpoint = "/api/register/";
  const form = new FormData(e.target);
  let data = Object.fromEntries(form.entries());
  e.preventDefault();
  if (e.target.childElementCount < 5) endpoint = "/api/login/";
  data = await fetchWithToken(glob_endp, endpoint, "POST", data);
  if (data == "Error") return;
  e.target.reset();

  if (endpoint == "/api/register/") {
    raiseWarn("Please verify your email", "alert");
    return updateUrl("login", "push");
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
  console.log(data);
  if (data.error) {
    raiseWarn("User logged out");
    return updateUrl("login", "push");
  } else if (data.game_id !== undefined) startGame(data.game_id);
  else if (data.tournament_id !== undefined) {
    playTournament(data.tournament_id);
  } else {
    data.map((n) => {
      if (n != "game_id" && notContainer)
        notContainer.innerHTML =
          components.notification_elem(n) + notContainer.innerHTML;
    });
  }
  if (data.length && notifier) notifier.classList.remove("hide");
}

function makeSocket(endpoint, socketMethod) {
  const socket = new WebSocket(`ws://127.0.0.1:8000/${endpoint}`);
  if (endpoint) makeSocket.latest = socket;
  socket.onerror = (e) => {
    raiseWarn("User logged out");
    return updateUrl("login", "push");
  };

  socket.onopen = function (event) {
    console.log("WebSocket is open now.");
  };

  socket.onmessage = socketMethod;

  socket.onclose = function (event) {
    console.log("WebSocket is closed now.");
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
    header.innerHTML = /*html*/ `
			<label class="img_label" for="games">
				<img id="logo" src="./assets/42.svg" alt="logo" />
			</label>
			<input class="hide togglers" type="checkbox" id="menu"/>
			<nav>
				${["Friends", "Chats", "Games", "logout"]
          .map((a) => {
            return this["menu_item"](a);
          })
          .join("\n")}
			</nav>
			<label class="img_label" for="menu" tabindex="1">
				<img id="logo" src="assets/avatars/${
          user_data?.avatar ? user_data.avatar : "user.svg"
        }" alt="logo" />
			</label>
		`;
    return header;
  },
  card: (s) => {
    return /*html*/ `<h1>${s}</h1>`;
  },
  chat_banner: function (user) {
    return /* html */ `
    <div class="chatBanner">
    ${icons.back("friendChat")}
      <label class="friendData">
        <img src="${user.avatar}" alt="${user.name}"/>
        <h6>${user.name}</h6>
      </label>
      <div class="controls">
        ${icons.challengeIcon}
        ${icons.block}
      </div>
    </div>
    `;
  },
  user_label: function (user, name, index) {
    if (name == "search_friends") name = "myFriends";
    return /* html */ `
			<input id="${
        user.first_name + name + user.id
      }" type="radio" class="chat_member hide" name="${name}" value="${
      user?.id
    }"/>
			<label onKeyDown="selction(event)" for="${
        user.first_name + name + user.id
      }" class="user_label ${!index ? " bubble" : ""}" tabindex="0">
				<img src="${"./assets/avatars/" + user.avatar}" alt="${user.first_name}"/>
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
  warning: function (error, type) {
    return /* html */ `
      <div onclick="removeElement(this)" class="warn ${type}" tabindex="0">${
      icons[type + "Icon"]
    }<p>${error}</p></div>
    `;
  },
  profile: function (user = {}) {
    const choices = {
      accepted: ["remove"],
      pending:
        user.last_action != user_data?.id ? ["accept", "decline"] : ["cancel"],
      "": ["invite"],
    };
    return /* html */ `
		<section id="userProfile">
    ${
      Object.keys(user).length
        ? /* html */ `
        <div class="userBanner">
        ${icons.back("myFriends")}
          <img src="${"./assets/avatars/" + user.avatar}" alt="${
            user.first_name
          }"/>
          <div class="userInfo">
          <h3>${user.first_name} ${user.last_name}</h3>
          <p>${user.email}</p>
          <div class="relManager">
          ${choices[user.relationship]
            .map((action) => {
              return /* html */ `<button onclick="network(this)" class='button' value="${action}_${user.id}">${action}</button>`;
            })
            .join("\n")}
          </div>
        </div>
    </div>`
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
        console.log(to_go)
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
              const updateCont = document.getElementById("userProfile");
              response = await fetchWithToken(
                glob_endp,
                `${"/friend/profile/"}${to_go[2]}/`
              );
              if (response == "Error") return;
              response.user = {
                relationship: response.rel,
                last_action: response.last_action_by,
                ...response.user,
              };
              updateCont.innerHTML = components["profile"](response.user)
                .trim()
                .split("\n")
                .slice(1, -1)
                .join("\n");
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
        <div id="notiList"></div>
    `;
    return not;
  },
  notification_elem: function (noti) {
    const myIcon =
      (noti.type != "invitation" ? "invitation" : "invitation") + "Icon";
    return /* html */ `
    <input type="radio" class="hide noti_member togglers" name="nots" id="${
      noti.type
    }_${noti.sender.first_name}_${noti.sender.id}_${noti.id}"/>
    <label for="${noti.type}_${noti.sender.first_name}_${noti.sender.id}_${
      noti.id
    }" class="notiLabel" tabindex="0">
      <img src="${"./assets/avatars/" + noti.sender.avatar}" alt="${
      noti.sender.first_name
    }"/>
      ${icons[myIcon]}
      <p>${noti.description}</p>
    </label>
  `;
  },
};

function logout(e) {
  e.preventDefault();
  localStorage.removeItem("user_data");
  user_data = undefined;
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
    if (makeSocket.latest) {
      makeSocket.latest.close();
      makeSocket.latest = undefined;
    }
  }
}

const pages = {
  "/": {
    data: /*html*/ `
			<section id="page">
			<label class="img_label" for="/">
				<img id="logo" src="./assets/42.svg" alt="logo" />
			</label>
		<section>
			<h1>JOIN - CHAT - PLAY</h1>
			<p>Join us - Chat with your friends - Play!</p>
		</section>
		<section class="indent">
			<label for="signin" class="button">Sign in</label>
			<label for="loginin" class="button">Login</label>
			<span></span>
			<label for="" class="button" onclick="auth42()">Continue with 42</label>
		</section>

			</section>
		`,
    id: "landing_page",
    func: () => {},
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
      let data;
      if (compo == "profile") {
        response = await fetchWithToken(
          glob_endp,
          `${endpoint}${e.target.value}/`
        );

        if (response == "Error") return;
        data = response;
        response.user = {
          relationship: response.rel,
          last_action: response.last_action_by,
          ...response.user,
        };
        data = response.user;
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
            ["block", "challenge"].indexOf(e.target.id) > -1 ||
            ["block", "challenge"].indexOf(e.target.parentElement.id) > -1
          ) {
            let action =
              ["block", "challenge"].indexOf(e.target.id) > -1
                ? e.target.id
                : e.target.parentElement.id;
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

const updateUrl = (path = "/", mode = "", targetId = "") => {
  const app = document.getElementById("landing");
  const main = document.getElementsByTagName("main")[0];
  const myForm = document.getElementById("messenger");
  if (makeSocket.latest) {
    makeSocket.latest.close();
    makeSocket.latest = undefined;
  }

  // if (myForm) myForm.removeEventListener("submit", sendMessage);
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
  } else if (!pages[path].glob && app.childElementCount > 2) {
    document.getElementsByTagName("header")[0]?.remove();
    document.getElementById("notification")?.remove();
    background.classList.remove("myblur");
  }
  document.querySelector(`.select`)?.classList.remove("select");
  app.querySelector(`[for="${id}"`)?.classList.add("select");
  if (targetId.length) {
    let timer = setInterval(() => {
      const target = main.querySelector("#" + targetId);
      if (target) {
        target.checked = true;
        target.dispatchEvent(new Event("change", { bubbles: true }));
        clearInterval(timer);
      }
    }, 10);
  }
  loader.classList.add("hide");
  loader.classList.remove("show");
};

document.body.onload = () => {
  const path = window.location.pathname;
  user_data = JSON.parse(localStorage.getItem("user_data"));
  loader.classList.add("show");
  loader.classList.remove("hide");
  if (!user_data && ["login", "signin", "/"].indexOf(path) < 0) {
    raiseWarn("User logged out");
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
