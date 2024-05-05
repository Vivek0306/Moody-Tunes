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

  function playSongAndStore(uri, emotion, name, duration, image) {
    fetch(`/store_songs?uri=${uri}&emotion=${emotion}&name=${name}&duration=${duration}&image=${image}`)
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Failed to store song');
        }
      })
      .then(data => {
        console.log('Song stored successfully:', data);
        // After storing the song, proceed with playing
        playSong(uri);
      })
      .catch(error => {
        console.error('Error storing song:', error);
      });
  }

function addPlaylist(uri, name, duration, image){
  fetch(`/add_playlist?uri=${uri}&name=${name}&duration=${duration}&image=${image}`)
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Failed to add playlist');
      }
    })
    .then(data => {
      console.log('Playlist added successfully:', data);
      // Redirect to /user_playlist
      window.location.href = '/user_playlist';
    })
    .catch(error => {
      console.error('Error storing song:', error);
    });
}