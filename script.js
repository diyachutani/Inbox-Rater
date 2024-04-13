// script.js
document.addEventListener('DOMContentLoaded', function() {
    // Get references to the navigation links
    var inboxLink = document.querySelector('a[href="#inbox"]');
    var settingsLink = document.querySelector('a[href="#settings"]');
    var feedbackLink = document.querySelector('a[href="#feedback"]');
    var iframe = document.querySelector('iframe');
  
    // Add click event listeners to the navigation links
    inboxLink.addEventListener('click', function(event) {
      event.preventDefault(); // Prevent default anchor link behavior
      loadIframe('login.html'); // Load the inbox page in the iframe
    });
  
    settingsLink.addEventListener('click', function(event) {
      event.preventDefault();
      loadIframe('settings.html'); // Load the settings page in the iframe
    });
  
    feedbackLink.addEventListener('click', function(event) {
      event.preventDefault();
      loadIframe('feedback.html'); // Load the feedback page in the iframe
    });
  
    // Function to load the specified page in the iframe
    function loadIframe(pageUrl) {
      // Check if the iframe is already displaying the specified page
      if (iframe.src === pageUrl) {
        // If yes, reload the iframe to reset its state
        iframe.contentWindow.location.reload(true);
      } else {
        // If not, load the specified page in the iframe
        iframe.src = pageUrl;
      }
    }
  });
  