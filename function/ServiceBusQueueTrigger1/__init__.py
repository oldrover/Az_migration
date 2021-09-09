import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info(f"Python ServiceBus queue trigger processed message: {notification_id}")

    # Get connection to database

    connection = psycopg2.connect(dbname='techconfdb', user='postgresuser@db-migration', password='Postgres1', host='db-migration.postgres.database.azure.com')
    cursor = connection.cursor()

    try:

        # Get notification message and subject from database using the notification_id
        notification_query = cursor.execute(f"SELECT message, subject FROM notification WHERE id = {notification_id}")

        # Get attendees email and name
        cursor.execute("SELECT first_name, last_name, email FROM attendee;")
        attendees = cursor.fetchall()

        # Loop through each attendee and send an email with a personalized subject

        for attendee in attendees:
            Mail(f"{'admin@techconf.com'}, {attendee[2]}, {notification_query}")

        notification_completed_date = datetime.utcnow()

        notification_status = f"Notified {len(attendee)} attendees"

        # Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        
        update_query = cursor.execute(f"UPDATE notification SET status = '{notification_status}', completed_date = '{notification_completed_date}' WHERE id = {notification_id};")        


    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # Close connection
        connection.commit()