// This script sends the text from the form to the server using a POST request

document.getElementById('textForm').onsubmit = function(event) {
    event.preventDefault();  // Prevent the form from submitting in the traditional way
    const textField = document.getElementById('textField');
    const text = textField.value;

    fetch('http://localhost:5000/api/name', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `text=${encodeURIComponent(text)}`  // Encode the text as form data
    }).then(response => {
        if (response.ok) {
            console.log("Text submitted successfully.");
            textField.value = '';  // Optionally clear the text field
        }
    }).catch(error => console.error("Error:", error));
};