# Import required libraries
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def CO2e(total_spam):
    """
    This function calculates the Carbon emissions (CO2e) from each of the mail boxes.
    The CO2e values are estimated in: https://carbonliteracy.com/the-carbon-cost-of-an-email/
    Spam emails have a CO2e of 0.03 g
    Small emails (defined as having a file size < 100 KB) have a CO2e of 0.3 g
    Large emails (defined as having a file size > 100 KB) have a CO2e of 17 g
    
    Args:
        total_spam (integer): The total number of emails in the spam mail box.
    Returns:
        carbon_spam (float): The estimated CO2e produced from spam emails.
        carbon_unread (float): The estimated CO2e produced from unread emails.
        carbon_read (float): The estimated CO2e produced from read emails.
    """
    # Defines boundary of small email as 100000 bytes (100 KB)
    small_email = 100000
    carbon_unread = 0
    carbon_read = 0

    carbon_spam = 0.03 * total_spam

    unread_emails_dict = {
        "email1": {"file_size": 100, "email_content": "Hello, this is email 1."},
        "email2": {"file_size": 150, "email_content": "Hello, this is email 2."},
    }

    # Calculate the total CO2e of the unread emails
    # email holds key of dictionary, info holds the values of the key (i.e. the file size and email content)
    for email, info in unread_emails_dict.items():
        file_size = info["file_size"]
        email_content = info["email_content"]

        # Determines the carbon footprint of the email based on if it is a large or small email
        if file_size < small_email:
            carbon_unread = 0.3 + carbon_unread

        elif file_size > small_email:
            carbon_unread = 17 + carbon_unread
            
    read_emails_dict = {
        "email1": {"file_size": 100, "email_content": "Hello, this is email 1."},
        "email2": {"file_size": 150, "email_content": "Hello, this is email 2."},
    }

    # Calculate the total CO2e of the read emails
    for email, info in read_emails_dict.items():
        file_size = info["file_size"]
        email_content = info["email_content"]

        # Determines the carbon footprint of the email based on if it is a large or small email
        if file_size < small_email:
            carbon_read = 0.3 + carbon_read

        elif file_size > small_email:
            carbon_read = 17 + carbon_read
          
    return carbon_spam, carbon_unread, carbon_read

total_spam = 10
total_unread = 10
total_read = 10
total_emails = total_spam + total_unread + total_read
# Determine the CO2e values for the mail boxes
CO2e_spam, CO2e_unread, CO2e_read = CO2e(total_spam)

CO2e_total = CO2e_spam + CO2e_unread + CO2e_read

email_data = {
    '': ['Spam', 'Unread', 'Read' , 'Total'],
    'Number of emails in mail box': [total_spam, total_unread, total_read, total_emails],
    'Carbon emissions (CO2e) /g': [CO2e_spam, CO2e_unread, CO2e_read, CO2e_total]
}

# The panda data frame
df = pd.DataFrame(email_data)

# Creates the pdf
pdf_filename = 'CO2e_emails.pdf'
pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)

# Convert panda data frame to list of lists
email_table_data = [df.columns.tolist()] + df.values.tolist()

# Defines the table style
style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)])

# Create a table and apply style
table = Table(email_table_data)
table.setStyle(style)

# Add the table to the PDF
pdf.build([table])

print(f"PDF saved as {pdf_filename}")