function setDimentions(game) {
  const dash = document.getElementById("game_dash");

  window_width = window.innerWidth - 40;
  window_height = window.innerHeight - 130;

  if (game.aspect > 1 && window_height <= window_width) {
    if (window_width / game.aspect > window.innerHeight - 130)
      window_width = window_height * game.aspect;
    else window_height = window_width / game.aspect;
  }
  game.height = window_height * 0.2;
  game.width = game.height / 10;
  game.settings = { axis: "y", depends: "height" };
  dash.classList.remove("rotate_stats");
  if (window_height > window_width) {
    dash.classList.add("rotate_stats");
    [window_width, window_height] = [window_height, window_width];
    if (game.aspect > 1) {
      window_height = window_width / game.aspect;
    }
    game.height = window_height * 0.2;
    game.width = game.height / 10;
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
      -game.ball.ballMoveY,
      game.ball.ballMoveX,
    ];
    game.settings = { axis: "x", depends: "width" };
    // game.ball.speed = window_width * 0.02;
  }
  let w = window_width;
  let h = window_height;
  if (game.settings.axis == "x") {
    w = window.innerWidth - 40;
    h = window.innerHeight - 130;
    if (game.aspect > 1) w = window_width / game.aspect;
  }
  game.oppoPaddle.speed = window_height * 0.02;
  game.playerPaddle.speed = window_height * 0.02;
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
  if (window.innerHeight > window.innerWidth && mypong.canvas.height > mypong.canvas.width) {
    mypong.ball.ballX = window_height / 2;
    mypong.ball.ballY = window_width / 2;
    if (mypong.ball.mirror == -1) {
      mypong.ball.ballMoveY *= -1;
      if (window.innerHeight > window.innerWidth && !mypong.opIsMobile) {
        mypong.ball.ballMoveX *= -1;
      }
    };
  } else {
    if (mypong.ball.mirror == -1) {
      mypong.ball.ballMoveX *= -1;
      if (window.innerHeight <= window.innerWidth && mypong.opIsMobile)
        mypong.ball.ballMoveY *= -1
    };
  }
  // if (game.rev < 0) {
  //   [game.ball.ballMoveX, game.ball.ballMoveY] = [
  //     game.ball.ballMoveY,
  //     game.ball.ballMoveX,
  //   ];
  // }
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
  console.log(winner.id, loser.id)
  winner.container.classList.add("winner");
  loser.container.classList.add("loser");
  document.getElementById("game_dash").classList.add("game_over");
  if (startGame.tournamentSocket) {
    pos = 0;
    tournamentInfo.matches.map((match, index) => {
      if (
        match.filter((m) => {
          return m.id == winner.id;
        }).length
      )
        pos = index;
    });
    console.log({
      winner: [pos, winner.id],
    });
    startGame.tournamentSocket.send(
      JSON.stringify({
        winner: [pos, winner.id],
      })
    );
    let timer = setTimeout(() => {
      playTournament(-1);
      clearTimeout(timer);
    }, 5000);
  } else {
    let timer = setTimeout(() => {
      updateUrl("games", "");
      clearTimeout(timer);
    }, 5000);
  }
}

function server(e, mypong) {
  data = JSON.parse(e.data);
  console.log(data);
  if (data.start) {
    mypong.ball.moves = data.start;
    resetBall(mypong);
    if (window.innerHeight > window.innerWidth && mypong.canvas.height > mypong.canvas.width) {
      mypong.playerPaddle.x = (window_height - mypong.width) / 2;
      mypong.oppoPaddle.x = (window_height - mypong.width) / 2;
    } else {
      mypong.playerPaddle.y = (window_height - mypong.height) / 2;
      mypong.oppoPaddle.y = (window_height - mypong.height) / 2;
    }
    let timer = setTimeout(() => {
      mypong.stop = 0;
      clearTimeout(timer);
    }, 5000);
    raiseWarn("Your match is about to start", "alert")
    timer = setTimeout(() => {
      loader.classList.add("hide");
      loader.classList.remove("show");
      mypong.launch();
      clearTimeout(timer);
    }, 3000)
  } else if (data.aspect) {
    let { w, h, mobile } = { ...data.aspect };
    let diff = +(window_height / h);
    if (diff == 1) diff = window_width / w;
    let aspect = +(w / h);
    if (diff > 1) mypong.aspect = aspect;
    if (window.innerHeight > window.innerWidth) {
      mypong.oppoPaddle = new Paddle(
        window_width - mypong.width,
        mypong.playerPaddle.y,
        mypong.oppoPaddle.id,
        mypong.playerPaddle.color,
        window_height * 0.02,
        "opp_player",
        mypong.oppoPaddle.data
      );
      if (w >= h) mypong.rev = -1;
      mypong.opIsMobile = mobile
    }
    mypong.ball.ballX = window_width / 2;
    mypong.ball.ballY = window_height / 2;
    setDimentions(mypong);
    if (window.innerHeight <= window.innerWidth)
      mypong.oppoPaddle = new Paddle(
        window_width - mypong.width,
        mypong.playerPaddle.y,
        mypong.oppoPaddle.id,
        mypong.playerPaddle.color,
        window_height * 0.02,
        "opp_player",
        mypong.oppoPaddle.data
      );
    if (diff > 1) {
      mypong.scale = w / window_width;
      if (mypong.scale < 1) mypong.scale = window_width / w;
    }
    mypong.socket.send(JSON.stringify({ ready: "" }));
  } else if (data.key) changePosOpp(mypong, data.key);
  else if (data.locked) {
    setDimentions(mypong);
    mypong.socket.send(JSON.stringify({ w: window_width, h: window_height, mobile: window.innerHeight > window_width }));
  } else if (data.opponent) {
    clearTimeout(mypong.timeout)
    if (data.view) mypong.ball.mirror = -1;
    mypong.oppoPaddle.id = data.opponent.id;
    mypong.oppoPaddle.data = data.opponent.data;
    document
      .getElementById("opp_player")
      .firstElementChild.nextElementSibling.setAttribute(
        "src",
        "/assets/avatars/" + data.opponent.avatar.replace("/", "")
      );
  } else if (data.game_over != undefined) {
      if (data.game_over.length) {
        mypong.oppoPaddle.score = -1;
        mypong.maxScore = mypong.playerPaddle.score;
      }
    gameOver(mypong);
  }
}

function Game(x, y, color, endpoint = "", maxScore) {
  this.canvas = document.getElementById("game_canvas");
  this.socket = makeSocket(endpoint, (event) => {
    server(event, this);
  });
  this.aspect = 1;
  this.scale = 1;
  this.stop = 1;
  this.rev = 1;
  this.width = window_width * 0.02;
  this.maxScore = maxScore;
  this.height = window_height * 0.2;
  this.timout;
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
    ball.ballX += ball.ballMoveX * game.scale;
    ball.ballY += ball.ballMoveY * game.scale;
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
          <img src="../assets/avatars/${user_data.avatar.replace("/", "")}"/>
          <p class="score">0</p>
        </div>
        <div class="player_stats" id="opp_player">
          <p class="score">0</p>
          <img src="../assets/avatars/${user_data.avatar.replace("/", "")}"/>
        </div>
      </div>
      <canvas id="game_canvas" width="${window.innerWidth - 40}" height="${window.innerHeight - 130
    }"></canvas>
  `;
  const cont = document.querySelector("#game_page");
  cont.innerHTML = statsBoard;
  cont.classList.add("in_game");
  cont.classList.remove("tournament_board");
  mypong = new Game(0, 0, "#31dede", `game/${id}`, 1);
  mypong.timeout = setTimeout(() => {
    clearTimeout(mypong.timeout)
    updateUrl('games', '')
  }, 15000)
  loader.classList.add("show");
  loader.classList.remove("hide");
  if (window.innerWidth < window.innerHeight)
    document.getElementById("game_dash").classList.add("rotate_stats");
}

function tournamentInfo(e) {
  const data = JSON.parse(e.data);
  console.log(data);
  if (data.locked) {
    loader.classList.add("hide");
    loader.classList.remove("show");
    let cont = document.getElementsByClassName("tournament");
    for (let i = 0; i < cont.length; i++) {
      data.locked[i].map((el, index) => {
        cont[i]
          .querySelector(".player_img" + (index + 1))
          .setAttribute(
            "src",
            "../assets/avatars/" + el.avatar.replace("/", "")
          );
      });
    }
    if (!tournamentInfo.matches.length) tournamentInfo.matches = data.locked;
  } else if (data.game_index !== undefined) {
    clearTimeout(startGame.timer)
    loader.classList.add("hide");
    loader.classList.remove("show");
    // raiseWarn("Your game is about to start", "alert");
    startGame(data.game_index);
  }
}

function playTournament(endpoint) {
  let socket;
  if (!tournamentInfo.matches) tournamentInfo.matches = [];
  else socket = startGame.tournamentSocket;
  if (endpoint != -1) {
    loader.classList.add("show");
    loader.classList.remove("hide");
  }
  if (!startGame.tournamentSocket) {
    socket = makeSocket(`tournament/${endpoint}`, tournamentInfo);
    startGame.tournamentSocket = socket;
  }
  if (endpoint != -1) {
    startGame.timer = setTimeout(() => {
      updateUrl('games', '')
      clearTimeout(startGame.timer)
    }, 20000);
  }
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
  if (notiSocket && !notiSocket.readyState) {
    const interval = setInterval(() => {
      if (notiSocket.readyState) {
        notiSocket.send(JSON.stringify(choice));
        clearInterval(interval);
      }
    }, 100);
  } else notiSocket.send(JSON.stringify(type));
}
