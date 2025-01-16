document.getElementById('forgotPasswordForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var email = document.getElementById('email').value;
    var errorBox = document.getElementById('errorBox');
    errorBox.innerText = ''; // Clear any previous error message

    // Send AJAX request to check if the email exists
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/check_email', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.exists) {
                // Send email with password reset link
                sendResetEmail(email);
            } else {
                errorBox.innerText = 'User with this email does not exist.';
            }
        }
    };
    xhr.send(JSON.stringify({ email: email }));
});

function sendResetEmail(email) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/send_reset_email', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            alert('OTP for resseting password sent to ' + email);
        }
    };
    xhr.send(JSON.stringify({ email: email }));
}