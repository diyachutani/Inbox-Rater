// script.js
document.addEventListener('DOMContentLoaded', function() {
    const inboxSection = document.getElementById('inbox');
    const emailDetailSection = document.getElementById('email-detail');
    const settingsSection = document.getElementById('settings');
    const feedbackSection = document.getElementById('feedback');
  
    // Mock data for demonstration
    const emails = [
      { id: 1, subject: 'Meeting Reminder', sender: 'john@example.com', rating: 4 },
      { id: 2, subject: 'Weekly Newsletter', sender: 'newsletter@example.com', rating: 3 },
      { id: 3, subject: 'Urgent: Action Required', sender: 'urgent@example.com', rating: 5 },
    ];
  
    // Get the email list container
    const emailList = document.getElementById('email-list');
  
    // Function to populate email list
    function populateEmailList() {
      emails.forEach(email => {
        const emailItem = document.createElement('li');
        emailItem.classList.add('email-item');
        emailItem.innerHTML = `
          <strong>${email.sender}</strong>: ${email.subject} (Rating: ${email.rating})
        `;
        emailList.appendChild(emailItem);
  
        // Add click event listener to show email detail
        emailItem.addEventListener('click', () => {
          showEmailDetail(email);
        });
      });
    }
  
    // Function to show email detail
    function showEmailDetail(email) {
      // Hide inbox section and show email detail section
      inboxSection.style.display = 'none';
      emailDetailSection.style.display = 'block';
  
      // Populate email detail section
      document.getElementById('email-content').innerHTML = `
        <strong>Subject:</strong> ${email.subject}<br>
        <strong>Sender:</strong> ${email.sender}<br>
        <strong>Rating:</strong> ${email.rating}<br>
        <!-- Add more details here as needed -->
      `;
  
      // You can also include buttons for actions like marking as important, archiving, etc.
    }
  
    // Add event listener to navigation links to show corresponding sections
    document.querySelectorAll('nav a').forEach(link => {
      link.addEventListener('click', function(event) {
        event.preventDefault();
        const targetSectionId = this.getAttribute('href').substring(1);
        const targetSection = document.getElementById(targetSectionId);
  
        // Hide all sections
        [inboxSection, emailDetailSection, settingsSection, feedbackSection].forEach(section => {
          section.style.display = 'none';
        });
  
        // Show target section
        targetSection.style.display = 'block';
      });
    });
  
    // Populate email list initially
    populateEmailList();
  });
  
  