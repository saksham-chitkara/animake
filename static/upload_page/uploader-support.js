// ADD THE FUNCTION TO LOAD THE IMAGE CONTENTS AND PASS THEM ONTO THE DATABASE
var files = [];
var count = 0;

function filePicker() {
    var input = document.createElement('input');
    input.type = 'file';
    input.accept = "image/jpeg, image/jpg, image/png";

    input.multiple = true; // Allows selecting multiple files
    input.style.display = 'none'; // Hide the input element

    document.body.appendChild(input);

    input.click();

    // When files are selected, handle the onchange event
    input.onchange = function(event) {
        var selectedFiles = event.target.files; // Get the selected files

        var fileList = document.getElementById('file-box');

        if(selectedFiles.length > 0){
            document.getElementById("msg").style.display = "none";
            document.getElementById("img").style.display = "none";

            var newFiles = Array.from(selectedFiles);
            files.push(...newFiles);

            console.log(files)

            for (var i = 0; i < selectedFiles.length; i++) {
                var file = selectedFiles[i];
                var id1 = "div" + (count);
                
                var sc = "";
                if(file.type == 'image/jpeg' || file.type == 'image/jpg') {
                    sc = "./static/upload_page/136524.png";
                }else if (file.type == 'image/png') {
                    sc = "./static/upload_page/png.png";
                }

                var listItem = document.createElement('div');
                listItem.setAttribute("id", id1); // id1, id2, id3
                listItem.setAttribute("class", "fields");

                var icon = document.createElement('img');
                icon.setAttribute("width", "10%");
                icon.setAttribute("height", "60%");
                icon.setAttribute("class", "format-i");
                icon.setAttribute("src", sc);

                var filep = document.createElement('p');
                filep.setAttribute("class", "img-name");
                filep.innerText = file.name;

                var filesp = document.createElement('p');
                filesp.setAttribute("class", "img-size");
                filesp.innerText = ((file.size / 1024).toFixed(2)) + " KB";

                var icon2 = document.createElement('img');
                icon2.setAttribute("width", "5%");
                icon2.setAttribute("height", "10%");
                icon2.setAttribute("class", "format-i");
                icon2.setAttribute("src", "./static/upload_page/canvas.png");
                icon2.setAttribute("id", "" + count);

                icon2.onclick = function(event){
                    var ic=event.target;
                    var idc=ic.id;
                    var del=document.getElementById("div"+idc);

                    files[idc] = -1;
                    console.log(files)

                    del.remove();

                    if(document.getElementById("file-box").children.length == 2){
                        document.getElementById("msg").style.display = "block";
                        document.getElementById("img").style.display = "block";
                    }
                };

                listItem.appendChild(icon);
                listItem.appendChild(filep);
                listItem.appendChild(filesp);
                listItem.appendChild(icon2);

                fileList.appendChild(listItem);
                count ++;
            }
        }
        // Remove the input element from the DOM
        input.remove();
    };
}

function dragoverhandler(event) {
    event.preventDefault();
}

function drophandler(event) {
    event.preventDefault();
    const files = event.dataTransfer.files;

    // Handle dropped files
    handleFiles(files);
}

function handleFiles(filesd) {
    var fileList = document.getElementById('file-box');

    document.getElementById("msg").style.display = "none";
    document.getElementById("img").style.display = "none";

    var newFiles = Array.from(filesd);
    files.push(...newFiles);

    console.log(files)

    for (const file of filesd) {
        var id1 = "div" + count;
        
        var sc = "";
        if(file.type == 'image/jpeg' || file.type == 'image/jpg') {
            sc = "./static/upload_page/136524.png";
        }else if (file.type == 'image/png') {
            sc = "./static/upload_page/png.png";
        }

        var listItem = document.createElement('div');
        listItem.setAttribute("id", id1); // id1, id2, id3
        listItem.setAttribute("class", "fields");

        var icon = document.createElement('img');
        icon.setAttribute("width", "10%");
        icon.setAttribute("height", "60%");
        icon.setAttribute("class", "format-i");
        icon.setAttribute("src", sc);

        var filep = document.createElement('p');
        filep.setAttribute("class", "img-name");
        filep.innerText = file.name;

        var filesp = document.createElement('p');
        filesp.setAttribute("class", "img-size");
        filesp.innerText = ((file.size / 1024).toFixed(2)) + " KB";

        var icon2 = document.createElement('img');
        icon2.setAttribute("width", "5%");
        icon2.setAttribute("height", "10%");
        icon2.setAttribute("class", "format-i");
        icon2.setAttribute("src", "./static/upload_page/canvas.png");
        icon2.setAttribute("id", "" + count);

        icon2.onclick = function(event){
            var ic=event.target;
            var idc=ic.id;
            var del=document.getElementById("div"+idc);

            files[idc] = -1;
            console.log(files)

            del.remove();

            if(document.getElementById("file-box").children.length == 2){
                
                document.getElementById("msg").style.display = "block";
                document.getElementById("img").style.display = "block";
            }
        };

        listItem.appendChild(icon);
        listItem.appendChild(filep);
        listItem.appendChild(filesp);
        listItem.appendChild(icon2);

        fileList.appendChild(listItem);

        count ++;
    }
}

let user_name = document.getElementById('username').value;
let access_token = document.getElementById('access_token').value;

function upl_files(){
    files2 = []
    files.forEach(element => {
        if(element != -1) {
            files2.push(element);
        }
    });
    if (files2.length > 0) {
        showOverlayAndSpinner();

        var formData = new FormData();
        formData.append('username', user_name);
        files2.forEach(function(file) {
            formData.append('file', file);
        });
        sendFormData(formData);
    } else {
        alert('Please select at least one file.');
    }
};

function sendFormData(formData) {
    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(response => {
        hideOverlayAndSpinner();
        
        window.alert("Images Uploaded Successfully!");
        window.location.href = "/create-video?access_token=" + access_token; 
    }).catch(error => {
        hideOverlayAndSpinner();
        console.error('Error:', error);
    });
}