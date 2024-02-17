document.addEventListener('DOMContentLoaded', function () {
  const videoElements = document.querySelectorAll('.mse-video');
  const urlInputs = document.querySelectorAll('.mse-url');

  videoElements.forEach((videoEl, index) => {
    const mseUrl = urlInputs[index].value;
    startPlay(videoEl, mseUrl);
  });

  function startPlay(videoEl, url) {
    const mseQueue = [];
    let mseSourceBuffer;
    let mseStreamingStarted = false;

    const mse = new MediaSource();
    videoEl.src = window.URL.createObjectURL(mse);

    mse.addEventListener('sourceopen', function () {
      const ws = new WebSocket(url);
      ws.binaryType = 'arraybuffer';
      ws.onopen = function (event) {
        console.log('Connected to WebSocket');
      };
      ws.onmessage = function (event) {
        const data = new Uint8Array(event.data);
        if (data[0] === 9) {
          let mimeCodec;
          const decodedArr = data.slice(1);
          if (window.TextDecoder) {
            mimeCodec = new TextDecoder('utf-8').decode(decodedArr);
          } else {
            mimeCodec = Utf8ArrayToStr(decodedArr);
          }
          mseSourceBuffer = mse.addSourceBuffer('video/mp4; codecs="' + mimeCodec + '"');
          mseSourceBuffer.mode = 'segments';
          mseSourceBuffer.addEventListener('updateend', pushPacket);
        } else {
          readPacket(event.data);
        }
      };
    }, false);

    function pushPacket() {
      let packet;
      if (!mseSourceBuffer.updating) {
        if (mseQueue.length > 0) {
          packet = mseQueue.shift();
          mseSourceBuffer.appendBuffer(packet);
        } else {
          mseStreamingStarted = false;
        }
      }
      if (videoEl.buffered.length > 0) {
        if (typeof document.hidden !== 'undefined' && document.hidden) {
          // no sound, browser paused video without sound in background
          videoEl.currentTime = videoEl.buffered.end((videoEl.buffered.length - 1)) - 0.5;
        }
      }
    }

    function readPacket(packet) {
      if (!mseStreamingStarted) {
        mseSourceBuffer.appendBuffer(packet);
        mseStreamingStarted = true;
        return;
      }
      mseQueue.push(packet);
      if (!mseSourceBuffer.updating) {
        pushPacket();
      }
    }

    videoEl.addEventListener('pause', () => {
      if (videoEl.currentTime > videoEl.buffered.end(videoEl.buffered.length - 1)) {
        videoEl.currentTime = videoEl.buffered.end(videoEl.buffered.length - 1) - 0.1;
        videoEl.play();
      }
    });
  }
});

// UTF-8 decoder function
function Utf8ArrayToStr(array) {
  let out, i, len, c;
  let char2, char3;

  out = "";
  len = array.length;
  i = 0;
  while(i < len) {
    c = array[i++];
    switch(c >> 4)
    {
      case 0: case 1: case 2: case 3: case 4: case 5: case 6: case 7:
        // 0xxxxxxx
        out += String.fromCharCode(c);
        break;
      case 12: case 13:
        // 110x xxxx   10xx xxxx
        char2 = array[i++];
        out += String.fromCharCode(((c & 0x1F) << 6) | (char2 & 0x3F));
        break;
      case 14:
        // 1110 xxxx  10xx xxxx  10xx xxxx
        char2 = array[i++];
        char3 = array[i++];
        out += String.fromCharCode(((c & 0x0F) << 12) |
                      ((char2 & 0x3F) << 6) |
                      ((char3 & 0x3F) << 0));
        break;
    }
  }

  return out;
}
