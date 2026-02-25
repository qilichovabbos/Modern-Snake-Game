const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let cw = canvas.width = window.innerWidth;
let ch = canvas.height = window.innerHeight;

const CELL = 22;
let snake = [{x:10, y:10}];
let dir = {x:1, y:0};
let food = {x:5, y:5};
let score = 0;
let gameOver = false;

const overlay = document.getElementById("overlay");
const startBtn = document.getElementById("startBtn");

startBtn.onclick = () => {
  overlay.style.display = "none";
  init();
  requestAnimationFrame(gameLoop);
}

function init() {
  snake = [{x:10, y:10}];
  dir = {x:1, y:0};
  spawnFood();
  score = 0;
  gameOver = false;
}

function spawnFood() {
  food.x = Math.floor(Math.random() * (cw/CELL));
  food.y = Math.floor(Math.random() * (ch/CELL));
}

window.addEventListener("keydown", e => {
  if(e.key==="ArrowUp" && dir.y!==1) dir={x:0,y:-1};
  if(e.key==="ArrowDown" && dir.y!==-1) dir={x:0,y:1};
  if(e.key==="ArrowLeft" && dir.x!==1) dir={x:-1,y:0};
  if(e.key==="ArrowRight" && dir.x!==-1) dir={x:1,y:0};
});

function gameLoop(){
  if(gameOver) return;
  update();
  draw();
  setTimeout(()=>requestAnimationFrame(gameLoop), 1000/10);
}

function update() {
  let head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};
  
  // wall collision
  if(head.x<0 || head.y<0 || head.x>=cw/CELL || head.y>=ch/CELL){
    endGame();
    return;
  }

  // self collision
  if(snake.some(s => s.x===head.x && s.y===head.y)){
    endGame();
    return;
  }

  snake.unshift(head);

  // food
  if(head.x===food.x && head.y===food.y){
    score++;
    spawnFood();
  } else {
    snake.pop();
  }
}

function draw() {
  ctx.clearRect(0,0,cw,ch);
  
  // draw snake
  snake.forEach((s,i)=>{
    ctx.fillStyle=i===0?'#54ffd6':'#7c59ff';
    ctx.fillRect(s.x*CELL, s.y*CELL, CELL-2, CELL-2);
  });

  // draw food
  ctx.fillStyle = '#dc232d';
  ctx.fillRect(food.x*CELL, food.y*CELL, CELL-2, CELL-2);

  // draw score
  ctx.fillStyle = '#fff';
  ctx.font = "20px Segoe UI";
  ctx.fillText("Score: "+score, 10, 30);
}

function endGame(){
  gameOver=true;
  alert("Game Over! Score: "+score);
  // send score to Telegram bot
  if(window.Telegram.WebApp){
    Telegram.WebApp.sendData(JSON.stringify({score}));
  }
}