const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Game settings
const GRAVITY = 0.6;
const JUMP_POWER = -12;
const ROLL_SPEED = 5;
const SPEED_INCREMENT = 0.002;
const INITIAL_SPEED = 5;

// Dino character
let dino = {
  x: 50,
  y: 150,
  width: 40,
  height: 40,
  velocityY: 0,
  grounded: true,
  rolling: false,
};

// Obstacles
let obstacles = [];
let gameSpeed = INITIAL_SPEED;
let score = 0;

// Controls
let keys = {};
window.addEventListener("keydown", (e) => (keys[e.code] = true));
window.addEventListener("keyup", (e) => (keys[e.code] = false));

// Game loop
function update() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Gravity and jumping
  if (!dino.rolling) dino.velocityY += GRAVITY;
  dino.y += dino.velocityY;

  // Keep Dino within ground level
  if (dino.y >= 150) {
    dino.y = 150;
    dino.velocityY = 0;
    dino.grounded = true;
  }

  // Jump
  if (keys["Space"] && dino.grounded && !dino.rolling) {
    dino.velocityY = JUMP_POWER;
    dino.grounded = false;
  }

  // Roll (shrinks the dino temporarily)
  if (keys["ArrowDown"] && dino.grounded) {
    dino.rolling = true;
    dino.height = 20;
  } else {
    dino.rolling = false;
    dino.height = 40;
  }

  // Move obstacles
  for (let i = 0; i < obstacles.length; i++) {
    obstacles[i].x -= gameSpeed;
    if (obstacles[i].x + obstacles[i].width < 0) {
      obstacles.splice(i, 1);
      score++;
    }
  }

  // Spawn obstacles
  if (Math.random() < 0.02) {
    let type = Math.random() < 0.5 ? "vault" : "roll";
    obstacles.push({
      x: canvas.width,
      y: 150,
      width: type === "vault" ? 30 : 60,
      height: type === "vault" ? 30 : 20,
      type: type,
    });
  }

  // Check collisions
  for (let obstacle of obstacles) {
    if (
      dino.x < obstacle.x + obstacle.width &&
      dino.x + dino.width > obstacle.x &&
      dino.y < obstacle.y + obstacle.height &&
      dino.y + dino.height > obstacle.y
    ) {
      alert("Game Over! Score: " + score);
      document.location.reload();
    }
  }

  // Increase speed over time
  gameSpeed += SPEED_INCREMENT;

  // Draw Dino
  ctx.fillStyle = "green";
  ctx.fillRect(dino.x, dino.y, dino.width, dino.height);

  // Draw Obstacles
  ctx.fillStyle = "red";
  for (let obstacle of obstacles) {
    ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
  }

  // Draw score
  ctx.fillStyle = "white";
  ctx.font = "20px Arial";
  ctx.fillText("Score: " + score, 20, 30);

  requestAnimationFrame(update);
}

update();
