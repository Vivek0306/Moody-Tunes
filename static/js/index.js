const video = document.getElementById('video');
const vidPlayDiv = document.querySelector('.vid-play');
const overlayCanvas = document.getElementById('overlayCanvas');
const emotionDiv = document.getElementById('emotion-div');


var camState = true;
var detected_emotion = "random songs";
var socket = io.connect('http://127.0.0.1:5000');
socket.on('connect', function () {
  console.log("SOCKET CONNECTED")
})

navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
Promise.all([
  faceapi.loadFaceLandmarkModel("http://127.0.0.1:5000/static/models/"),
  faceapi.loadFaceRecognitionModel("http://127.0.0.1:5000/static/models/"),
  faceapi.loadTinyFaceDetectorModel("http://127.0.0.1:5000/static/models/"),
  faceapi.loadFaceLandmarkModel("http://127.0.0.1:5000/static/models/"),
  faceapi.loadFaceLandmarkTinyModel("http://127.0.0.1:5000/static/models/"),
  faceapi.loadFaceRecognitionModel("http://127.0.0.1:5000/static/models/"),
  faceapi.loadFaceExpressionModel("http://127.0.0.1:5000/static/models/"),
])
  .then(startVideo)
  .catch(err => console.error(err));

function startVideo() {
  navigator.getUserMedia(
    {
      video: {}
    },
    stream => video.srcObject = stream,
    err => console.error(err)
  )
}

video.addEventListener('play', () => {
  const canvas = faceapi.createCanvasFromMedia(video);
  canvas.className = 'face-canvas';
  canvas.style.position = 'absolute';
  canvas.style.top = '10';
  canvas.style.left = '10';
  vidPlayDiv.append(canvas, video);
  const displaySize = { width: video.width, height: video.height };
  faceapi.matchDimensions(canvas, displaySize);


  setInterval(async () => {
    const detections = await faceapi
      .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks()
      .withFaceExpressions();
    socket.emit('my event', {
      data: detections
    })
    if (detections.length > 0) {
      const emotions = detections[0].expressions;
      const emotion = Object.keys(emotions).reduce((a, b) => emotions[a] > emotions[b] ? a : b);
      detected_emotion = emotion;
      emotionDiv.textContent = `Detected Emotion: ${emotion}`;
    } else {
      console.log("ERROR OCCURED")
      emotionDiv.textContent = "No face detected";
    }


    const resizedDetections = faceapi.resizeResults(detections, displaySize);
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    faceapi.draw.drawDetections(canvas, resizedDetections);
    faceapi.draw.drawFaceLandmarks(canvas, resizedDetections);
    faceapi.draw.drawFaceExpressions(canvas, resizedDetections);
  }, 100)


  function stopVideo() {
    camState = false;
    video.pause();
    $.ajax({
      type: 'GET',
      url: '/fetch_songs',
      data: { emotion: detected_emotion },
      success: function (response) {
        const musicListContainer = document.getElementById('music-list');
        musicListContainer.innerHTML = '';
        const titleElement = document.createElement('div');
        titleElement.innerHTML = `
          <div class="text-center">
            <h4>Recommending songs for <span style="font-weight: 800; color: #1DB954;">${detected_emotion}</span>  mood</h4>
          </div>
        `
        musicListContainer.appendChild(titleElement);
        response.forEach(track => {
          console.log(track.name);
          const trackElement = document.createElement('div');
          trackElement.classList.add('p-2');
          trackElement.classList.add('my-2');
          trackElement.style.display = 'flex';
          trackElement.style.flexDirection = 'row';
          trackElement.style.gap = '24px';
          trackElement.style.backgroundColor = '#171717';
          trackElement.style.alignItems = 'center';
          trackElement.style.justifyContent = 'center';
          trackElement.style.borderRadius = '12px';
          trackElement.innerHTML = `
              <img src="${track.image_url}" height="65px" width="65px" alt="${track.name}">
              <div style="display: flex; flex-direction: row; justify-content: space-between; width: 100%; align-items: center;">
                  <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center;">
                      <p class="mt-2" style="font-weight: 600;">${track.name}</p>
                      <p class="mb-2">${(track.duration / 60000).toFixed(2)} mins</p>
                      <p class="mb-2">By ${track.artist}</p>
                  </div>
                    <div class="mx-4 play-icon" onclick="playSong('${track.song_url}')">
                      <span class="fa fa-play"></span>
                    </div>
              </div>
          `;

          // Append the track element to the music list container
          musicListContainer.appendChild(trackElement);
        });
        console.log('Received songs data:', response);
      },
      error: function (error) {
        console.error('Error fetching songs:', error);
      }
    });
    clearInterval(detectionInterval);
  }
  function startVideo() {
    const prevCanvas = document.querySelector('.face-canvas');
    if (prevCanvas && camState === false) {
      prevCanvas.remove();
    }
    camState = true;
    video.play();
  }

  document.getElementById('stopButton').addEventListener('click', stopVideo);
  document.getElementById('startButton').addEventListener('click', startVideo);

});


function playSong(uri) {
  fetch(`/play?uri=${uri}`)
    .then(response => response.json())
    .then(data => {
      const playerContent = document.createElement('div');
      playerContent.innerHTML = data.embed_html;

      const container = document.getElementById('player-container');
      container.innerHTML = '';

      container.appendChild(playerContent);
    })
    .catch(error => {
      console.error('Error fetching embed:', error);
    });
}