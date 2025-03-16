# Function to send email notification to manager
def send_email_notification(review_data):
    sender_email = "<SENDER EMAIL-ID"
    sender_password = "<APP PASSWORD>"
    manager_email = "<MANAGER EMAIL-ID"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = manager_email
    msg['Subject'] = "New Real-Time Hotel Review Alert"
    
    # Email body
    body = f"""
    Dear Manager,
    
    A new review has been submitted by a current guest:
    
    Customer ID: {review_data['customer_id']}
    Room Number: {review_data['room_number']}
    Rating: {review_data['Rating']}
    Review: {review_data['Review']}
    
    This requires your immediate attention as it's from a guest currently staying at the hotel.
    
    Hotel Review System
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Setup SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, manager_email, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email notification failed: {str(e)}")
        return False
    





         # If customer is currently staying, send email notification
                if currently_staying:
                    if send_email_notification(new_review):
                        st.info("The hotel manager has been notified of your review.")
                    else:
                        st.warning("Could not notify the manager, but your review was saved.")