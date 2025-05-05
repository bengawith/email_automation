document.getElementById("emailForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent default form submission

    let sendButton = document.getElementById("sendButton");
    let loadingMessage = document.getElementById("loading");

    sendButton.disabled = true;
    loadingMessage.style.display = "block";

    // Retrieve CSRF token from the hidden input field
    let csrfToken = document.querySelector("input[name='csrf_token']").value;

    fetch("/send_email", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken  // Send CSRF token in header
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            window.location.href = "/success";  // Redirect upon success
        } else {
            alert("Error: " + data.message);
            sendButton.disabled = false;
            loadingMessage.style.display = "none";
        }
    })
    .catch(error => {
        alert("Unexpected error occurred.");
        sendButton.disabled = false;
        loadingMessage.style.display = "none";
    });
});