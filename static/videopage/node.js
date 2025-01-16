canvas = document.getElementById('canvas');
ctx = canvas.getContext('2d');
video = document.getElementById('video');

pauseBtn = document.getElementById("pause");
pauseImg = document.getElementById("pauseimg");
stopImg = document.getElementById("stop_img");
rewindBtn = document.getElementById('rewind');
forwardBtn = document.getElementById('forward');

var isPaused = video.paused;

function rewind() {
    video.currentTime -= 5;
}

function forward() {
    video.currentTime += 5;
}

function pauseVideo() {
    if (isPaused) {
        pauseImg.src= "./static/videopage/pause.png";
        video.play();
    } else {
        pauseImg.src= "./static/videopage/play.png";
        video.pause();
    }
    isPaused = !isPaused;
}

function update(){
    stopImg.src = pauseImg.src;
}

setInterval(update, 1);

var durationDisplay = document.getElementById('duration_display');

function updateDurationDisplay() {
    var currentTime = video.currentTime;
    var minutes = Math.floor(currentTime / 60);
    var seconds = Math.floor(currentTime % 60);
    
    minutes = (minutes < 10) ? "0" + minutes : minutes;
    seconds = (seconds < 10) ? "0" + seconds : seconds;

    durationDisplay.textContent = minutes + ":" + seconds;
}

video.addEventListener('timeupdate', updateDurationDisplay);
rewindBtn.addEventListener('click', rewind);
forwardBtn.addEventListener('click', forward);
pauseBtn.addEventListener('click', pauseVideo);

video.addEventListener('play', function() {
    pauseImg.src= "./static/videopage/pause.png";
});

video.addEventListener('pause', function() {
    pauseImg.src = "./static/videopage/play.png";
});