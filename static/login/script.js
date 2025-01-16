function togglePasswordVisibility() {
    var passwordInput = document.getElementById('passwordInput');
    var img = document.getElementById('eyeimg');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        img.setAttribute('src', './static/login/eyecross.png');
    } else {
        passwordInput.type = 'password';
        img.setAttribute('src', './static/login/eye.png');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const inputFields = document.querySelectorAll(".input-container input");

    inputFields.forEach(function(inputField) {
        const label = inputField.nextElementSibling;

        inputField.addEventListener("focus", function() {
            label.style.top = "-2%";
            label.style.fontSize = "14px";
            label.style.color = "rgb(235, 65, 94)";
        });

        inputField.addEventListener("blur", function() {
            if (inputField.value === "") {
                label.style.top = "50%";
                label.style.fontSize = "16px";
                label.style.color = "#999";
            }
        });

        if (inputField.value !== "") {
            label.style.top = "-2%";
            label.style.fontSize = "14px";
            label.style.color = "rgb(235, 65, 94)";
        }
    });
});
