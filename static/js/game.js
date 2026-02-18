// Snake Game for Study Breaks
class SnakeGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.gridSize = 20;
        this.tileCount = 20;
        this.canvas.width = this.gridSize * this.tileCount;
        this.canvas.height = this.gridSize * this.tileCount;
        
        this.snake = [{x: 10, y: 10}];
        this.food = this.generateFood();
        this.dx = 0;
        this.dy = 0;
        this.score = 0;
        this.gameRunning = false;
        this.gameLoop = null;
        this.speed = 100; // ms per frame
        
        this.setupControls();
        this.updateScoreDisplay();
    }
    
    setupControls() {
        document.addEventListener('keydown', (e) => {
            if (!this.gameRunning && ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'w', 'a', 's', 'd'].includes(e.key)) {
                this.start();
            }
            
            switch(e.key) {
                case 'ArrowUp':
                case 'w':
                    if (this.dy === 0) { this.dx = 0; this.dy = -1; }
                    e.preventDefault();
                    break;
                case 'ArrowDown':
                case 's':
                    if (this.dy === 0) { this.dx = 0; this.dy = 1; }
                    e.preventDefault();
                    break;
                case 'ArrowLeft':
                case 'a':
                    if (this.dx === 0) { this.dx = -1; this.dy = 0; }
                    e.preventDefault();
                    break;
                case 'ArrowRight':
                case 'd':
                    if (this.dx === 0) { this.dx = 1; this.dy = 0; }
                    e.preventDefault();
                    break;
            }
        });
        
        // Touch controls for mobile
        let touchStartX = 0;
        let touchStartY = 0;
        
        this.canvas.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            if (!this.gameRunning) this.start();
        });
        
        this.canvas.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            const dx = touchEndX - touchStartX;
            const dy = touchEndY - touchStartY;
            
            if (Math.abs(dx) > Math.abs(dy)) {
                // Horizontal swipe
                if (dx > 0 && this.dx === 0) { this.dx = 1; this.dy = 0; }
                else if (dx < 0 && this.dx === 0) { this.dx = -1; this.dy = 0; }
            } else {
                // Vertical swipe
                if (dy > 0 && this.dy === 0) { this.dx = 0; this.dy = 1; }
                else if (dy < 0 && this.dy === 0) { this.dx = 0; this.dy = -1; }
            }
        });
    }
    
    generateFood() {
        let newFood;
        do {
            newFood = {
                x: Math.floor(Math.random() * this.tileCount),
                y: Math.floor(Math.random() * this.tileCount)
            };
        } while (this.snake.some(segment => segment.x === newFood.x && segment.y === newFood.y));
        return newFood;
    }
    
    start() {
        if (this.gameRunning) return;
        this.gameRunning = true;
        this.gameLoop = setInterval(() => this.update(), this.speed);
        document.getElementById('gameStatus').textContent = 'Playing';
        document.getElementById('gameStatus').style.color = '#10b981';
    }
    
    pause() {
        if (!this.gameRunning) return;
        this.gameRunning = false;
        clearInterval(this.gameLoop);
        document.getElementById('gameStatus').textContent = 'Paused';
        document.getElementById('gameStatus').style.color = '#f59e0b';
    }
    
    reset() {
        this.pause();
        this.snake = [{x: 10, y: 10}];
        this.food = this.generateFood();
        this.dx = 0;
        this.dy = 0;
        this.score = 0;
        this.updateScoreDisplay();
        this.draw();
        document.getElementById('gameStatus').textContent = 'Ready';
        document.getElementById('gameStatus').style.color = '#8b5cf6';
    }
    
    update() {
        // Move snake
        const head = {x: this.snake[0].x + this.dx, y: this.snake[0].y + this.dy};
        
        // Check wall collision
        if (head.x < 0 || head.x >= this.tileCount || head.y < 0 || head.y >= this.tileCount) {
            this.gameOver();
            return;
        }
        
        // Check self collision
        if (this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
            this.gameOver();
            return;
        }
        
        this.snake.unshift(head);
        
        // Check food collision
        if (head.x === this.food.x && head.y === this.food.y) {
            this.score += 10;
            this.updateScoreDisplay();
            this.food = this.generateFood();
            // Increase speed slightly
            if (this.score % 50 === 0 && this.speed > 50) {
                this.speed -= 5;
                clearInterval(this.gameLoop);
                this.gameLoop = setInterval(() => this.update(), this.speed);
            }
        } else {
            this.snake.pop();
        }
        
        this.draw();
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#0f172a';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid
        this.ctx.strokeStyle = '#1e293b';
        this.ctx.lineWidth = 0.5;
        for (let i = 0; i <= this.tileCount; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.gridSize, 0);
            this.ctx.lineTo(i * this.gridSize, this.canvas.height);
            this.ctx.stroke();
            
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.gridSize);
            this.ctx.lineTo(this.canvas.width, i * this.gridSize);
            this.ctx.stroke();
        }
        
        // Draw snake
        this.snake.forEach((segment, index) => {
            const gradient = this.ctx.createLinearGradient(
                segment.x * this.gridSize, segment.y * this.gridSize,
                (segment.x + 1) * this.gridSize, (segment.y + 1) * this.gridSize
            );
            
            if (index === 0) {
                gradient.addColorStop(0, '#8b5cf6');
                gradient.addColorStop(1, '#6366f1');
            } else {
                gradient.addColorStop(0, '#6366f1');
                gradient.addColorStop(1, '#4f46e5');
            }
            
            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(
                segment.x * this.gridSize + 1,
                segment.y * this.gridSize + 1,
                this.gridSize - 2,
                this.gridSize - 2
            );
            
            // Add glow effect to head
            if (index === 0) {
                this.ctx.shadowBlur = 15;
                this.ctx.shadowColor = '#8b5cf6';
                this.ctx.fillRect(
                    segment.x * this.gridSize + 1,
                    segment.y * this.gridSize + 1,
                    this.gridSize - 2,
                    this.gridSize - 2
                );
                this.ctx.shadowBlur = 0;
            }
        });
        
        // Draw food
        const foodGradient = this.ctx.createRadialGradient(
            this.food.x * this.gridSize + this.gridSize / 2,
            this.food.y * this.gridSize + this.gridSize / 2,
            0,
            this.food.x * this.gridSize + this.gridSize / 2,
            this.food.y * this.gridSize + this.gridSize / 2,
            this.gridSize / 2
        );
        foodGradient.addColorStop(0, '#fbbf24');
        foodGradient.addColorStop(1, '#f59e0b');
        
        this.ctx.fillStyle = foodGradient;
        this.ctx.shadowBlur = 10;
        this.ctx.shadowColor = '#fbbf24';
        this.ctx.beginPath();
        this.ctx.arc(
            this.food.x * this.gridSize + this.gridSize / 2,
            this.food.y * this.gridSize + this.gridSize / 2,
            this.gridSize / 2 - 2,
            0,
            Math.PI * 2
        );
        this.ctx.fill();
        this.ctx.shadowBlur = 0;
    }
    
    updateScoreDisplay() {
        document.getElementById('gameScore').textContent = this.score;
        document.getElementById('gameLength').textContent = this.snake.length;
    }
    
    gameOver() {
        this.pause();
        document.getElementById('gameStatus').textContent = 'Game Over!';
        document.getElementById('gameStatus').style.color = '#ef4444';
        
        // Save high score
        const highScore = parseInt(localStorage.getItem('snakeHighScore') || '0');
        if (this.score > highScore) {
            localStorage.setItem('snakeHighScore', this.score.toString());
            document.getElementById('highScore').textContent = this.score;
            this.showMessage('🎉 New High Score!');
        }
    }
    
    showMessage(msg) {
        const messageEl = document.getElementById('gameMessage');
        messageEl.textContent = msg;
        messageEl.style.opacity = '1';
        setTimeout(() => {
            messageEl.style.opacity = '0';
        }, 2000);
    }
}

// Initialize game when panel is opened
let snakeGame = null;

function initGame() {
    if (!snakeGame) {
        snakeGame = new SnakeGame();
        const highScore = parseInt(localStorage.getItem('snakeHighScore') || '0');
        document.getElementById('highScore').textContent = highScore;
    }
}

// Game controls
function startGame() {
    if (snakeGame) snakeGame.start();
}

function pauseGame() {
    if (snakeGame) snakeGame.pause();
}

function resetGame() {
    if (snakeGame) snakeGame.reset();
}
