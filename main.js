const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const WIDTH = 1280;
const HEIGHT = 720;
const AREA_SIZE = 50;
const AREA_POSITION = 30;
const FPS = 30;
const FUTURE_ARROW_LENGTH = 150;
const CONTROLER_POSITION_START = 940;
const SCALE_FACTOR_SPEED = 0.06;
const SCALE_FACTOR_GAIN = 0.02;
const BLACK = 0;
const WHITE = 100;

let background_image = new Image();
background_image.src = 'res/background.png';

const offScreenCanvas = document.createElement('canvas');
offScreenCanvas.width = WIDTH;
offScreenCanvas.height = HEIGHT;
const offScreenCtx = offScreenCanvas.getContext('2d');

let sprite = {
    image: new Image(),
    x: WIDTH / 2,
    y: HEIGHT / 2,
    angle: -90,
    speed: 0,
    gain: 0,
    pause: false
};

sprite.image.src = 'res/sprite.png';

document.getElementById('speedSlider').addEventListener('input', (e) => {
    sprite.speed = e.target.value * SCALE_FACTOR_SPEED;
    document.getElementById('speedValue').textContent = e.target.value;
});

document.getElementById('gainSlider').addEventListener('input', (e) => {
    sprite.gain = e.target.value * SCALE_FACTOR_GAIN;
    document.getElementById('gainValue').textContent = e.target.value;
});

function drawSprite() {
    ctx.save();
    ctx.translate(sprite.x, sprite.y);
    ctx.rotate(sprite.angle * Math.PI / 180);
    ctx.drawImage(sprite.image, -sprite.image.width / 2, -sprite.image.height / 2);
    ctx.restore();
}

function rotateSprite(angle) {
    sprite.angle += angle;
}

function moveForwardSprite(speed, angle) {
    rotateSprite(angle);
    radian_angle = sprite.angle * Math.PI / 180;
    sprite.x += speed * Math.cos(radian_angle);
    sprite.y += speed * Math.sin(radian_angle);
}

function updateSprite() {
    if (!sprite.pause) {
        const brightness = getBrightness();
        const error = (BLACK + WHITE) / 2 - brightness;
        moveForwardSprite(sprite.speed, sprite.gain * error);
    }
}

function drawBackground() {
    ctx.drawImage(background_image, 0, 0);
}

function getBrightness() {
    const frontX = sprite.x + AREA_POSITION * Math.cos(sprite.angle * Math.PI / 180);
    const frontY = sprite.y + AREA_POSITION * Math.sin(sprite.angle * Math.PI / 180);
    const frontRect = {
        x: frontX - AREA_SIZE / 2,
        y: frontY - AREA_SIZE / 2,
        width: AREA_SIZE,
        height: AREA_SIZE
    };

    const imageData = offScreenCtx.getImageData(frontRect.x, frontRect.y, frontRect.width, frontRect.height);
    const data = imageData.data;

    let totalBrightness = 0;
    let totalCount = 0;

    for (let y = 0; y < AREA_SIZE; y++) {
        for (let x = 0; x < AREA_SIZE; x++) {
            const index = (y * AREA_SIZE + x) * 4;
            const r = data[index];
            const g = data[index + 1];
            const b = data[index + 2];

            // 円形マスクを適用
            const dx = x - AREA_SIZE / 2;
            const dy = y - AREA_SIZE / 2;
            if (dx * dx + dy * dy <= (AREA_SIZE / 2) * (AREA_SIZE / 2)) {
                const brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b;
                totalBrightness += brightness;
                totalCount++;
            }
        }
    }

    const averageBrightness = totalBrightness / totalCount;
    const brightnessPercentage = (averageBrightness / 255) * 100;
    return Math.round(brightnessPercentage);
}

function drawBrightnessArea() {
    const frontX = sprite.x + AREA_POSITION * Math.cos(sprite.angle * Math.PI / 180);
    const frontY = sprite.y + AREA_POSITION * Math.sin(sprite.angle * Math.PI / 180);

    ctx.beginPath();
    ctx.arc(frontX, frontY, AREA_SIZE / 2, 0, 2 * Math.PI);
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 2;
    ctx.stroke();
}

function drawFuturePath() {
    const futurePath = [];
    const tempSprite = {
        x: sprite.x,
        y: sprite.y,
        angle: sprite.angle
    };

    const speed = document.getElementById('speedSlider').value * SCALE_FACTOR_SPEED / 3;
    const gain = document.getElementById('gainSlider').value * SCALE_FACTOR_GAIN;
    const brightness = getBrightness();
    const error = (BLACK + WHITE) / 2 - brightness;
    const angle = error * gain;

    for (let i = 0; i < FUTURE_ARROW_LENGTH; i++) {
        const radian_angle = tempSprite.angle * Math.PI / 180;
        tempSprite.x += speed * Math.cos(radian_angle);
        tempSprite.y += speed * Math.sin(radian_angle);
        tempSprite.angle += angle;
        futurePath.push({ x: tempSprite.x, y: tempSprite.y });
    }

    if (futurePath.length > 1) {
        ctx.beginPath();
        ctx.moveTo(futurePath[0].x, futurePath[0].y);
        for (let i = 1; i < futurePath.length; i++) {
            ctx.lineTo(futurePath[i].x, futurePath[i].y);
        }
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw arrowhead
        const arrowTip = futurePath[futurePath.length - 1];
        const arrowAngle = tempSprite.angle * Math.PI / 180;
        const arrowSize = 10;
        ctx.beginPath();
        ctx.moveTo(
            arrowTip.x + arrowSize * Math.cos(arrowAngle),
            arrowTip.y + arrowSize * Math.sin(arrowAngle)
        );
        ctx.lineTo(
            arrowTip.x + arrowSize * Math.cos(arrowAngle + 2.5),
            arrowTip.y + arrowSize * Math.sin(arrowAngle + 2.5)
        );
        ctx.lineTo(
            arrowTip.x + arrowSize * Math.cos(arrowAngle - 2.5),
            arrowTip.y + arrowSize * Math.sin(arrowAngle - 2.5)
        );
        ctx.closePath();
        ctx.fillStyle = 'red';
        ctx.fill();
    }
}

function drawControler() {
    const brightness = getBrightness();
    const error = (BLACK + WHITE) / 2 - brightness;
    const pidAngle = error * sprite.gain;

    document.getElementById('brightness-info').textContent = `反射光: ${brightness}`;
    document.getElementById('error-info').textContent = `中間値ー反射光: ${error}`;
    document.getElementById('pid-angle-info').textContent = `PID角度: ${(pidAngle / SCALE_FACTOR_GAIN).toFixed(1)}`;
}

function draw() {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);
    drawSprite();
    drawBrightnessArea();
    drawFuturePath();
    drawControler(); // Add this line to update the controller info
    requestAnimationFrame(draw);
}

function loop() {
    updateSprite();
    console.log(getBrightness());
    setTimeout(loop, 1000 / FPS);
}

canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    sprite.x = e.clientX - rect.left;
    sprite.y = e.clientY - rect.top;
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') {
        sprite.angle -= 10;
    } else if (e.key === 'ArrowRight') {
        sprite.angle += 10;
    } else if (e.key === 'p') {
        sprite.pause = !sprite.pause;
    }
});

sprite.image.onload = () => {
    // drawBackground();
    backupBackground(); // Add this line to backup the background image data
};

background_image.onload = () => {
    offScreenCtx.drawImage(background_image, 0, 0); // Draw the background image once
    draw();
    loop();
};