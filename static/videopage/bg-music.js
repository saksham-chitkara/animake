function audio() {
    var input = document.createElement('input');
    input.type = 'file';
    input.accept = "audio/*";
    input.multiple = true; 
    input.style.display = 'none';

    input.addEventListener('change', function() {
        var files = this.files;
        if (files.length > 0) {
            for (var i = 0; i < files.length; i++) {
                handleFileUpload(files[i]);
            }
        }
    });
    input.click();
}

function handleFileUpload(file) {
    uname = document.getElementById("username").value;

    var formData = new FormData();
    formData.append('audio_file', file);

    showOverlayAndSpinner();
    fetch('/upload_audio/' + uname, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        hideOverlayAndSpinner();
        if (response.ok) {
            fetchAudioData();
            console.log('Audio file uploaded successfully.');
        } else {
            console.error('Error uploading audio file.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}