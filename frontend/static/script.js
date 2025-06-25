let video;
let resultado;

function startCameraRecognition() {
  video = document.getElementById('video');
  resultado = document.getElementById('resultado');

  navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
    .then(stream => {
      video.srcObject = stream;
      video.play();
      recognizeLoop();
      // Hide all buttons when recognition starts
      const buttons = document.querySelectorAll('button');
      buttons.forEach(btn => btn.style.display = 'none');
    })
    .catch(err => {
      resultado.textContent = 'Erro ao acessar a câmera: ' + err;
    });
}

function captureFrame() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg');
}

function recognizeLoop() {
  const imageData = captureFrame();

  fetch('/reconhecer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image: imageData })
  })
  .then(response => response.json())
  .then(data => {
    if (data.length === 0) {
      resultado.textContent = 'Nenhum rosto detectado.';
    } else {
      resultado.textContent = data.map(r => `${r.nome} (${(r.probabilidade * 100).toFixed(0)}%)`).join(', ');
    }
  });

  setTimeout(recognizeLoop, 2000);
}
