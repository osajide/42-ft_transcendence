function setDimentions(game) {
  const dash = document.getElementById("game_dash");
  window_width = window.innerWidth - 40;
  window_height = window.innerHeight - 130;
  if (game.resize > 1 && window_height < window_width) {
    if (window_width / game.resize > window.innerHeight - 130)
      window_width = window_height * game.resize;
    else window_height = window_width / game.resize;
  }
  game.width = window_width * 0.02;
  game.height = window_height * 0.2;
  game.settings = { axis: "y", depends: "height" };
  dash.classList.remove("rotate_stats");
  if (window_height > window_width) {
    dash.classList.add("rotate_stats");
    [window_width, window_height] = [window_height, window_width];
    if (game.resize > 1) {
      window_height = window_width / game.resize;
      game.width = window_width * 0.02;
    }
    game.height = window_height * 0.2;
    [game.width, game.height] = [game.height, game.width];
    [game.playerPaddle.x, game.playerPaddle.y] = [
      game.playerPaddle.y,
      game.playerPaddle.x,
    ];
    game.oppoPaddle.x = window_width - game.height;
    [game.oppoPaddle.x, game.oppoPaddle.y] = [
      game.oppoPaddle.y,
      game.oppoPaddle.x,
    ];
    [game.ball.ballX, game.ball.ballY] = [game.ball.ballY, game.ball.ballX];
    [game.ball.ballMoveX, game.ball.ballMoveY] = [
      game.ball.ballMoveY,
      game.ball.ballMoveX,
    ];
    game.settings = { axis: "x", depends: "width" };
    game.oppoPaddle.speed = window_height * 0.02;
    game.playerPaddle.speed = window_height * 0.02;
    // game.ball.speed = window_width * 0.02;
  }
  let w = window_width;
  let h = window_height;
  if (game.settings.axis == "x") {
    w = window.innerWidth - 40;
    h = window.innerHeight - 130;
    if (game.resize > 1) w = window_width / game.resize;
  }
  game.canvas.setAttribute("width", w);
  game.canvas.setAttribute("height", h);
  game.ball.ballSize = window_height * 0.02;
}

function Paddle(x, y, id, color, speed, scoreCont, data) {
  this.id = id;
  this.x = x;
  this.y = y;
  this.color = color;
  this.speed = speed;
  this.score = 0;
  this.data = data;
  this.container = document.getElementById(scoreCont);
}

function Ball(speed) {
  this.ballSize = window_height * 0.02;
  this.ballX = window_width / 2;
  this.ballY = window_height / 2;
  this.ballMoveX = speed;
  this.ballMoveY = speed;
  this.moves = [];
  this.mirror = 1;
}

function resetBall(game) {
  game.ball.ballMoveX = game.ball.moves[0].x;
  game.ball.ballMoveY = game.ball.moves[0].y;
  mypong.ball.ballX = window_width / 2;
  mypong.ball.ballY = window_height / 2;
  if (window.innerHeight > window.innerWidth) {
    mypong.ball.ballX = window_height / 2;
    mypong.ball.ballY = window_width / 2;
  }
  game.ball.moves.shift();
}

function gameOver(game) {
  cancelAnimationFrame(game.frameId);
  const winner =
    game.playerPaddle.score == game.maxScore
      ? game.playerPaddle
      : game.oppoPaddle;
  const loser =
    game.playerPaddle.id == winner.id ? game.oppoPaddle : game.playerPaddle;
  game.socket.send(
    JSON.stringify({
      stats: {
        winner: { id: winner.id, score: winner.score },
        loser: { id: loser.id, score: loser.score },
      },
    })
  );
  game.socket.close();
  game.socket = undefined;
  winner.container.classList.add("winner");
  loser.container.classList.add("loser");
  document.getElementById("game_dash").classList.add("game_over");
}

function server(e, mypong) {
  data = JSON.parse(e.data);
  console.log(data);
  if (data.start) {
    mypong.ball.moves = data.start;
    resetBall(mypong);
    if (window.innerHeight > window.innerWidth) {
      [mypong.ball.ballMoveX, mypong.ball.ballMoveY] = [
        -mypong.ball.ballMoveY,
        mypong.ball.ballMoveX,
      ];
      mypong.playerPaddle.x = (window_height - mypong.width) / 2;
      mypong.oppoPaddle.x = (window_height - mypong.width) / 2;
      if (mypong.ball.mirror == -1) mypong.ball.ballMoveY *= -1;
    } else {
      mypong.playerPaddle.y = (window_height - mypong.height) / 2;
      mypong.oppoPaddle.y = (window_height - mypong.height) / 2;
      if (mypong.ball.mirror == -1) mypong.ball.ballMoveX *= -1;
    }
    // let counter = 0
    // let timer = setInterval(() => {

    // }, 3500)
    loader.classList.add("hide");
    loader.classList.remove("show");
    mypong.launch();
  } else if (data.aspect) {
    let { w, h } = { ...data.aspect };
    let diff = +(window_height / h);
    if (diff == 1) diff = window_width / w;
    let scale = +(w / h);
    if (diff > 1) mypong.resize = scale;
    if (window.innerHeight > window.innerWidth)
      mypong.oppoPaddle = new Paddle(
        window_width * (1 - 0.02),
        mypong.playerPaddle.y,
        mypong.oppoPaddle.id,
        mypong.playerPaddle.color,
        window_height * 0.02,
        "opp_player",
        mypong.oppoPaddle.data
      );
    mypong.ball.ballX = window_width / 2;
    mypong.ball.ballY = window_height / 2;
    setDimentions(mypong);
    if (window.innerHeight < window.innerWidth)
      mypong.oppoPaddle = new Paddle(
        window_width * (1 - 0.02),
        mypong.playerPaddle.y,
        mypong.oppoPaddle.id,
        mypong.playerPaddle.color,
        window_height * 0.02,
        "opp_player",
        mypong.oppoPaddle.data
      );
    mypong.socket.send(JSON.stringify({ ready: "" }));
  } else if (data.key) changePosOpp(mypong, data.key);
  else if (data.locked) {
    setDimentions(mypong);
    mypong.socket.send(JSON.stringify({ w: window_width, h: window_height }));
  } else if (data.opponent) {
    if (data.view) mypong.ball.mirror = -1;
    mypong.oppoPaddle.id = data.opponent.id;
    mypong.oppoPaddle.data = data.opponent.data;
  }
}

function Game(x, y, color, endpoint = "", maxScore) {
  this.canvas = document.getElementById("game_canvas");
  this.socket = makeSocket(endpoint, (event) => {
    server(event, this);
  });
  this.resize = 1;
  this.stop = 0;
  this.width = window_width * 0.02;
  this.maxScore = maxScore;
  this.height = window_height * 0.2;
  this.playerPaddle = new Paddle(
    x,
    y,
    user_data.id,
    color,
    window_height * 0.02,
    "current_player",
    user_data
  );
  this.oppoPaddle = new Paddle(
    window_width * (1 - 0.02),
    y,
    -1,
    color,
    window_height * 0.02,
    "opp_player",
    {}
  );
  this.frameId;
  this.ball = new Ball(window_height * 0.02);
  this.press = null;
  this.settings = { axis: "y", depends: "height" };
  this.ctx = this.canvas.getContext("2d");
  this.launch = function () {
    document.getElementById("game_dash").classList.remove("hide");
    document.addEventListener("keydown", (e) => {
      this.press = e.key;
    });
    document.addEventListener("keyup", () => {
      this.press = null;
    });
    this.refresh();
  };
  this.refresh = function () {
    if (
      (this.playerPaddle.score == this.maxScore ||
        this.oppoPaddle.score == this.maxScore) &&
      this.socket
    ) {
      return gameOver(this);
    }
    this.clear();
    if (this.press) changePos(this);
    if (!this.stop) ballMovement(this);
    this.draw();
    this.frameId = requestAnimationFrame(() => {
      this.refresh();
    });
  };
  this.draw = function () {
    this.ctx.beginPath();
    this.ctx.arc(
      this.ball.ballX,
      this.ball.ballY,
      this.ball.ballSize,
      0,
      2 * Math.PI
    );
    this.ctx.fillStyle = "#fff";
    this.ctx.fill();
    this.ctx.closePath();
    this.ctx.fillStyle = color;
    this.ctx.fillRect(
      this.playerPaddle.x,
      this.playerPaddle.y,
      this.width,
      this.height
    );
    this.ctx.fillRect(
      this.oppoPaddle.x,
      this.oppoPaddle.y,
      this.width,
      this.height
    );
  };
  this.clear = function () {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  };
}

function changePosOpp(obj, press) {
  if (press == "ArrowUp" && obj.oppoPaddle[obj.settings.axis] >= 0) {
    obj.oppoPaddle[obj.settings.axis] -= obj.oppoPaddle.speed;
  } else if (
    press == "ArrowDown" &&
    obj.oppoPaddle[obj.settings.axis] + obj[obj.settings.depends] <=
      obj.canvas[obj.settings.depends]
  ) {
    obj.oppoPaddle[obj.settings.axis] += obj.oppoPaddle.speed;
  }
}

function changePos(obj) {
  let move = 0;
  if (obj.press == "ArrowUp" && obj.playerPaddle[obj.settings.axis] >= 0) {
    obj.playerPaddle[obj.settings.axis] -= obj.playerPaddle.speed;
    move = 1;
  } else if (
    obj.press == "ArrowDown" &&
    obj.playerPaddle[obj.settings.axis] + obj[obj.settings.depends] <=
      obj.canvas[obj.settings.depends]
  ) {
    obj.playerPaddle[obj.settings.axis] += obj.playerPaddle.speed;
    move = 1;
  }
  if (move) obj.socket.send(JSON.stringify({ key: obj.press }));
}

function scoreGoal(player, game) {
  game.stop = 1;
  player.score++;
  player.container.querySelector(".score").innerHTML = player.score;
  resetBall(game);
  let timer = setTimeout(() => {
    game.stop = 0;
    clearInterval(timer);
  }, 1000);
}

function ballMovement(game) {
  const ball = game.ball;
  const player = game.playerPaddle;
  const opponent = game.oppoPaddle;
  if (game.settings.axis == "y") {
    if (
      ball.ballY + ball.ballMoveY - ball.ballSize < 0 ||
      ball.ballY + ball.ballMoveY + ball.ballSize > game.canvas.height
    )
      //if the ball hits the top or bottom border
      ball.ballMoveY *= -1;
    else if (ball.ballX + ball.ballMoveX - ball.ballSize < game.width) {
      //if the ball hits the left border
      if (ball.ballY < player.y || ball.ballY > player.y + game.height) {
        scoreGoal(opponent, game);
      } else ball.ballMoveX *= -1;
    } else if (
      ball.ballX + ball.ballMoveX + ball.ballSize >
      game.canvas.width - game.width
    ) {
      //if the ball hits the right border
      if (ball.ballY < opponent.y || ball.ballY > opponent.y + game.height) {
        scoreGoal(player, game);
      } else ball.ballMoveX *= -1;
    }
  } else {
    if (
      ball.ballX + ball.ballMoveX - ball.ballSize < 0 ||
      ball.ballX + ball.ballMoveX + ball.ballSize > game.canvas.width
    ) {
      //if the ball hits the left or right border
      ball.ballMoveX *= -1;
    } else if (ball.ballY + ball.ballMoveY - ball.ballSize < game.height / 2) {
      //if the ball hits the top border
      if (ball.ballX < player.x || ball.ballX > player.x + game.width) {
        scoreGoal(opponent, game);
      } else ball.ballMoveY *= -1;
    } else if (
      ball.ballY + ball.ballMoveY + ball.ballSize >
      game.canvas.height - game.height / 2
    ) {
      //if the ball hits the bottom border
      if (ball.ballX < opponent.x || ball.ballX > opponent.x + game.width) {
        scoreGoal(player, game);
      } else ball.ballMoveY *= -1;
    }
  }
  if (!game.stop) {
    ball.ballX += ball.ballMoveX;
    ball.ballY += ball.ballMoveY;
  }
}

// function ballMovement(obj) {
//   if (
//     obj.ball.ballX + obj.ball.ballMoveX - obj.ball.ballSize < 0 ||
//     obj.ball.ballX + obj.ball.ballMoveX + obj.ball.ballSize > obj.canvas.width
//   )
//     obj.ball.ballMoveX *= -1;
//   if (
//     obj.ball.ballY + obj.ball.ballMoveY - obj.ball.ballSize < 0 ||
//     obj.ball.ballY + obj.ball.ballMoveY + obj.ball.ballSize > obj.canvas.height
//   )
//     obj.ball.ballMoveY *= -1;
//   obj.ball.ballX += obj.ball.ballMoveX;
//   obj.ball.ballY += obj.ball.ballMoveY;
// }

function startGame(id) {
  const statsBoard = /* html */ `
      <div id="game_dash" class="hide">
        <div class="player_stats" id="current_player">
          <img src="../assets/avatars/${user_data.avatar}"/>
          <p class="score">0</p>
        </div>
        <div class="player_stats" id="opp_player">
          <p class="score">0</p>
          <img src="../assets/avatars/${user_data.avatar}"/>
        </div>
      </div>
      <canvas id="game_canvas" width="${window.innerWidth - 40}" height="${
    window.innerHeight - 130
  }"></canvas>
  `;
  const cont = document.querySelector("#game_page");
  cont.innerHTML = statsBoard;
  cont.classList.add("in_game");
  cont.classList.remove("tournament_board");
  mypong = new Game(0, 0, "#31dede", `game/${id}`, 1);
  loader.classList.add("show");
  loader.classList.remove("hide");
  if (window.innerWidth < window.innerHeight)
    document.getElementById("game_dash").classList.add("rotate_stats");
}

function tournamentInfo(e) {
  this.matches = [];
  const data = JSON.parse(e.data);
  const players = document.getElementsByClassName("player_img");
  console.log(data, players);
  if (data.locked) {
    const cont = document.getElementsByClassName("tournament");
    this.matches = data.locked;
    for (i in cont) {
      data.locked[i].map((el, index) => {
        cont[0]
          .querySelector(".player_img" + (index + 1))
          .setAttribute("src", "../assets/avatars/" + el.avatar);
      });
    }
  }
}

function playTournament(endpoint) {
  const socket = makeSocket(`tournament/${endpoint}`, tournamentInfo);
  const board = /* html */ `
    <div class="tournament">
      <img src="../assets/avatars/user.svg" class="player_img player_img1">
      <img src="../assets/avatars/user.svg" class="player_img player_img5">
      <img src="../assets/avatars/user.svg" class="player_img player_img2">
      <img src="../assets/avatars/user.svg" class="player_img player_img7">
      <img src="../assets/avatars/user.svg" class="player_img player_img3">
      <img src="../assets/avatars/user.svg" class="player_img player_img6">
      <img src="../assets/avatars/user.svg" class="player_img player_img4">
      <span class="pair_link"></span>
      <span class="pair_link"></span>
    </div>
    <div class="tournament">
    <img src="../assets/avatars/user.svg" class="player_img player_img1">
    <img src="../assets/avatars/user.svg" class="player_img player_img5">
    <img src="../assets/avatars/user.svg" class="player_img player_img2">
    <img src="../assets/avatars/user.svg" class="player_img player_img7">
    <img src="../assets/avatars/user.svg" class="player_img player_img3">
    <img src="../assets/avatars/user.svg" class="player_img player_img6">
    <img src="../assets/avatars/user.svg" class="player_img player_img4">
      <span class="pair_link"></span>
      <span class="pair_link"></span>
    </div>
    `;
  const cont = document.querySelector("#game_page");
  cont.classList.remove("in_game");
  cont.classList.add("tournament_board");
  cont.innerHTML = board;
}

function game_choice(type) {
  const choice = {};
  choice[type] = "";
  console.log(type);
  if (!notiSocket.readyState) {
    const interval = setInterval(() => {
      if (notiSocket.readyState) {
        notiSocket.send(JSON.stringify(choice));
        clearInterval(interval);
      }
    }, 100);
  } else notiSocket.send(JSON.stringify(type));
}
