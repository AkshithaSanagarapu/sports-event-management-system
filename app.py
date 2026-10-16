from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash, make_response, render_template_string, session
from pymongo import MongoClient
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bson.objectid import ObjectId
from bcrypt import checkpw
import bcrypt
from datetime import datetime
import os

app = Flask(__name__)


# MongoDB connection
client = MongoClient(os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client['sportsmanagement']
organizers_collection = db['organizers']
students_collection = db['students']
events_collection = db['events']
notifications_collection = db["notifications"]
complaints_collection = db['complaints']
proposals_collection = db['ground_proposals']
oproposals_collection =db['organization_proposals)']
registrations_collection = db['registrations']
invoices_collection = db['invoices']

app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(32)


@app.route('/')
def main_screen():
    return render_template('main_screen.html')

"""NAV START"""
@app.route('/nav/admin_nav')
def admin_nav():
    return render_template('admin_nav.html')

@app.route('/s_nav')
def student_navigation():
    return render_template('s_nav.html')

@app.route('/e_nav')
def event_navigation():
    return render_template('e_nav.html')
"""NAV END"""

"""ADMIN START"""
# Dummy admin credentials for demonstration
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

@app.route('/admin/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Redirect to admin dashboard upon successful login
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid credentials. Please try again."
            return render_template('admin_login.html', error=error)
    return render_template('admin_login.html')

@app.route('/admin/admin_dashboard')
def admin_dashboard():    
    # Render admin dashboard template
    return render_template('admin_dashboard.html')

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the login page (you can change this URL to any desired page)
    return redirect(url_for('admin_login'))

"""ADMIN END"""

"""ADMIN OPERATION"""
# Route for rendering the add_event_organizer form
@app.route('/add_event_organizer', methods=['GET'])
def show_add_event_organizer_form():
    return render_template('add_event_organizer.html')


def generate_username(name):
    # Remove whitespace and convert name to lowercase
    name = name.strip().lower()
    # Remove any non-alphanumeric characters
    name = ''.join(char for char in name if char.isalnum())
    # Take the first 8 characters of the name as the username
    username = name[:8]
    return username

@app.route('/add_event_organizer', methods=['POST'])
def add_event_organizer():
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    address = request.form['address']

    # Generate unique username based on the input name
    username = generate_username(name)

    # Check if the generated username already exists
    existing_organizer = organizers_collection.find_one({'username': username})
    if existing_organizer:
        # If the username already exists, generate a new one by appending a random suffix
        username += ''.join(random.choices(string.digits, k=4))

    # Generate random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Store organizer data in MongoDB
    organizer_data = {
        'name': name,
        'email': email,
        'mobile': mobile,
        'address': address,
        'username': username,
        'password': hashed_password.decode('utf-8')  # Decode the hashed password to store as string
    }
    organizers_collection.insert_one(organizer_data)

    # Send login credentials to the provided email
    send_email(name, email, username, password)

    return redirect(url_for('show_add_event_organizer_form'))

def send_email(name, email, username, password):
    # Email configuration
    sender_email = os.environ.get('SMTP_EMAIL', '')
    sender_password = os.environ.get('SMTP_APP_PASSWORD', '')

    if not sender_email or not sender_password:
        app.logger.warning('SMTP not configured; email notification skipped.')
        return

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email  # Send email to the provided email address
    msg['Subject'] = 'Login Credentials'

    # Email body
    body = f'Hello {name},\n\nWELCOME TO GNITS COLLEGE,\n\nYour login credentials:\nUsername: {username}\nPassword: {password}'
    msg.attach(MIMEText(body, 'plain'))

    # SMTP server connection and sending email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

@app.route('/student_list')
def student_list():
    # Fetch all students from MongoDB
    students = students_collection.find()
    return render_template('student_list.html', students=students)

# Route to delete a student
@app.route('/delete_student/<string:student_id>', methods=['POST'])
def delete_student(student_id):
    # Delete the student from MongoDB based on the provided student_id
    students_collection.delete_one({'_id': ObjectId(student_id)})
    return redirect(url_for('student_list'))
"""ADMIN OPERATIONS END"""


"""ORGANIERS LIST"""
# Route for displaying organizers list
@app.route('/admin/organizers_list')
def organizers_list():
    # Fetch organizers from MongoDB
    organizers = list(organizers_collection.find())
    return render_template('organizers_list.html', organizers=organizers)

# Route for deleting an organizer
@app.route('/admin/delete_organizer/<string:organizer_id>', methods=['POST'])
def delete_organizer(organizer_id):
    # Delete organizer from MongoDB
    organizers_collection.delete_one({'_id': ObjectId(organizer_id)})
    return redirect(url_for('organizers_list'))
"""ORGANIERTS LIST"""



"""STUDENT SIGNUP"""
@app.route('/signup_student')
def signup_student_page():
    return render_template('student/signup_student.html')

@app.route('/signup/student', methods=['POST'])
def signup_student():
    name = request.form['name']
    gender = request.form['gender']
    roll_number = request.form['rollNumber']
    contact_number = request.form['contactNumber']
    email = request.form['email']
    branch = request.form['branch']
    academic_year = request.form['academicYear']
    address = request.form['address']
    password = request.form['password']

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Check if the student with the same roll number already exists
    existing_student = students_collection.find_one({'rollNumber': roll_number})
    if existing_student:
        return render_template('signup_failure.html', message='Student with this roll number already exists!')

    # Insert new student record in MongoDB
    student_data = {
        'name': name,
        'gender': gender,
        'rollNumber': roll_number,
        'contactNumber': contact_number,
        'email': email,
        'branch': branch,
        'academicYear': academic_year,
        'address': address,
        'password': hashed_password.decode('utf-8')  # Store hashed password
    }
    students_collection.insert_one(student_data)

    return render_template('student/signup_success.html', message='Student signup successful!')

"""STUDENT SIGNUP END"""

"""STUDENT LOGIN"""

@app.route('/signup_success')
def signup_success():
    return render_template('signup_success.html')

@app.route('/redirect_login')
def redirect_login():
    return redirect(url_for('login_student'))

@app.route('/login_student')
def login_student_page():
    return render_template('student/login_student.html')

@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch student from MongoDB
        student = students_collection.find_one({'email': email})

        if student and bcrypt.checkpw(password.encode('utf-8'), student['password'].encode('utf-8')):
            # Successful login
            session['logged_in'] = True  # Set session variable to indicate user is logged in
            session['user_id'] = str(student['_id'])  # Set user_id in session
            return redirect(url_for('student_dashboard'))
        else:
            # Invalid credentials
            return render_template('login_failure.html', message='Invalid email or password')

    # For GET requests, render the login page
    return render_template('student/login_student.html')

@app.route('/student_dashboard')
def student_dashboard():
    events = list(events_collection.find())
    # Check if the user is logged in
    if session.get('logged_in'):
        return render_template('student/student_dashboard.html', events=events)
    else:
        # If not logged in, redirect to the login page
        return redirect(url_for('login_student'))

@app.route('/s_notifications')
def s_notifications():
    notifications = notifications_collection.find()
    return render_template('student/s_notifications.html', notifications=notifications)

@app.route('/student_logout')
def student_logout():
    session.pop('logged_in', None)  # Remove 'logged_in' session variable
    return redirect(url_for('main_screen'))




"""STUDENT LOGIN END"""

"""ORGANIER LOGIN"""
@app.route('/event_organizer_login')
def event_organizer_login():
    return render_template('eventorganizer/event_organizer_login.html')

@app.route('/login/organizer', methods=['POST'])
def login_organizer():
    username = request.form['username']
    password = request.form['password']

    # Fetch event organizer from MongoDB
    organizer = organizers_collection.find_one({'username': username})

    if organizer is not None and bcrypt.checkpw(password.encode('utf-8'), organizer['password'].encode('utf-8')):
        # Clear any existing session data
        session.clear()
        # Store username in session
        session['username'] = username  
        # Redirect to event dashboard
        return redirect(url_for('event_dashboard'))  
    else:
        # Invalid credentials, render login failure template with message
        return render_template('login_failure.html', message='Incorrect username or password')
        


@app.route('/event_dashboard')
def event_dashboard():
    
    if 'username' in session:
        events = list(events_collection.find())
        return render_template('eventorganizer/event_dashboard.html', events=events)
    else:
        return redirect(url_for('eventorganizer/event_organizer_login'))

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        event_name = request.form['event_name']
        date = request.form['date']
        time = request.form['time']
        contact_number = request.form['contact_number']
        venue = request.form['venue']
        location = request.form['location']
        description = request.form['description']

        datetime_str = f"{date} {time}"
        event_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

        # Store event data in MongoDB
        event_data = {
            'event_name': event_name,
            'datetime': event_datetime,
            'contact_number': contact_number,
            'venue': venue,
            'location': location,
            'description': description
        }
        events_collection.insert_one(event_data)

        return redirect(url_for('event_added_successfully'))  # Redirect to the add event page after submission
    else:
        return render_template('eventorganizer/add_event.html')

@app.route('/event_added_successfully')
def event_added_successfully():
    return "Event added successfully!" 


@app.route('/event_list')
def event_list():
    # Fetch events from MongoDB
    search_query = request.args.get('search_query')
    if search_query:
        events = events_collection.find({
            '$or': [
                {'event_name': {'$regex': search_query, '$options': 'i'}},
                {'datetime': {'$regex': search_query, '$options': 'i'}},
                {'contact_number': {'$regex': search_query, '$options': 'i'}},
                {'venue': {'$regex': search_query, '$options': 'i'}},
                {'location': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}}
            ]
        })
    else:
        events = events_collection.find()
    return render_template('eventorganizer/event_list.html', events=events)


@app.route('/s_event_list')
def s_event_list():
    # Fetch events from MongoDB
    search_query = request.args.get('search_query')
    if search_query:
        events = events_collection.find({
            '$or': [
                {'event_name': {'$regex': search_query, '$options': 'i'}},
                {'datetime': {'$regex': search_query, '$options': 'i'}},
                {'contact_number': {'$regex': search_query, '$options': 'i'}},
                {'venue': {'$regex': search_query, '$options': 'i'}},
                {'location': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}}
            ]
        })
    else:
        events = events_collection.find()
    return render_template('student/s_event_list.html', events=events)

@app.route('/delete_event', methods=['POST'])
def delete_event():
    event_id = request.form['event_id']
    # Delete event from MongoDB
    events_collection.delete_one({'_id': ObjectId(event_id)})
    return redirect(url_for('event_list'))


@app.route('/update_event_status', methods=['POST'])
def update_event_status():
    data = request.json
    event_id = data.get('event_id')
    status = data.get('status')
    
    try:
        events_collection.update_one(
            {'_id': ObjectId(event_id)},
            {'$set': {'status': status}}
        )
        return jsonify({'message': 'Event status updated successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for rendering the add_notification form
@app.route('/add_notification', methods=['GET'])
def show_add_notification_form():
    return render_template('eventorganizer/add_notification.html')

# Route for handling the form submission
@app.route('/add_notification', methods=['POST'])
def add_notification():
    # Get form data
    notice = request.form['notice']
    file = request.files['file']
    photo = request.files['photo']

    # Save file uploads to server
    file_path = save_file_upload(file)
    photo_path = save_file_upload(photo)

    # Store notification data in MongoDB
    notification_data = {
        'notice': notice,
        'file_path': file_path,
        'photo_path': photo_path
    }
    notifications_collection.insert_one(notification_data)

    return redirect(url_for('show_add_notification_form'))

# Function to save file uploads to server
def save_file_upload(file):
    if file:
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        return file_path
    return None

@app.route('/notifications')
def notifications():
    notifications = notifications_collection.find()
    return render_template('eventorganizer/notifications.html', notifications=notifications)

# Route to handle file download
@app.route('/download_file/<file_id>')
def download_file(file_id):
    # Logic to fetch file path from MongoDB based on file_id
    file_path = ...  # Fetch file path from MongoDB using file_id
    return send_file(file_path, as_attachment=True)

# Route to handle notification deletion
@app.route('/delete_notification', methods=['POST'])
def delete_notification():
    notification_id = request.form['notification_id']
    # Logic to delete notification from MongoDB based on notification_id
    try:
        notifications_collection.delete_one({'_id': ObjectId(notification_id)})
        flash('Notification deleted successfully.', 'success')
    except:
        flash('Error deleting notification.', 'danger')
    return redirect(url_for('notifications'))


"""COMPLAINT"""
# Route to render the raise complaint form
@app.route('/raise_complaint', methods=['GET'])
def raise_complaint_form():
    return render_template('student/raise_complaint.html')

@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    # Check if the user is authenticated
    if 'user_id' not in session:
        flash('Please log in to submit a complaint.', 'error')
        return redirect(url_for('login_student'))  # Redirect to the login page

    # User is authenticated, proceed with complaint submission
    user_id = session['user_id']

    # Fetch user details from the student collection
    student_data = students_collection.find_one({'_id': ObjectId(user_id)})

    if student_data:
        # Extract user details from the student data
        name = student_data.get('name')
        branch = student_data.get('branch')
        roll_number = student_data.get('roll_number')
        
        # Get complaint details from the form
        complaint = request.form['complaint']

        # Store complaint data in MongoDB along with user details and current datetime
        complaint_data = {
            'name': name,
            'branch': branch,
            'roll_number': roll_number,
            'complaint': complaint,
            'datetime': datetime.now()
        }
        complaints_collection.insert_one(complaint_data)

        # Redirect to a success page or back to the complaint form
        return redirect(url_for('raise_complaint_form'))
    else:
        flash('User details not found.', 'error')
        return redirect(url_for('login_student'))
    
@app.route('/fetch_complaints')
def fetch_complaints():
    # Fetch complaints from MongoDB
    complaints = complaints_collection.find()
    return render_template('fetch_complaint.html', complaints=complaints)
"""COMPLAINT END"""


"""GROUND PROPOSAL"""
@app.route('/ground_proposal')
def ground_proposal_form():
    return render_template('ground_proposal.html')

@app.route('/submit_ground_proposal', methods=['POST'])
def submit_ground_proposal():
    # Get form data
    name = request.form['name']
    contact_number = request.form['contact_number']
    business_name = request.form['business_name']
    address = request.form['address']
    gps = request.form['gps']

    # Store proposal data in MongoDB
    proposal_data = {
        'name': name,
        'contact_number': contact_number,
        'business_name': business_name,
        'address': address,
        'gps': gps
    }
    proposals_collection.insert_one(proposal_data)

    # Redirect back to the ground proposal form after submission
    return redirect(url_for('ground_proposal_form'))

@app.route('/ground_proposal_success')
def ground_proposal_success():
    return "Ground proposal submitted successfully!"


@app.route('/ground_requests')
def ground_requests():
    # Fetch ground proposals from MongoDB
    proposals = list(proposals_collection.find())
    return render_template('ground_requests.html', proposals=proposals)
"""GROUND PRPOSAL END"""

"""ORGANIZATION PROPOSAL"""
@app.route('/organiztion_proposal')
def organization_proposal_form():
    return render_template('organization_proposal.html')

@app.route('/submit_organization_proposal', methods=['POST'])
def submit_organization_proposal():
    # Get form data
    name = request.form['name']
    contact_number = request.form['contact_number']
    business_name = request.form['business_name']
    address = request.form['address']
    gps = request.form['gps']

    # Store proposal data in MongoDB
    oproposal_data = {
        'name': name,
        'contact_number': contact_number,
        'business_name': business_name,
        'address': address,
        'gps': gps
    }
    oproposals_collection.insert_one(oproposal_data)

    # Redirect back to the ground proposal form after submission
    return redirect(url_for('organization_proposal_form'))

@app.route('/organization_proposal_success')
def organization_proposal_success():
    return "Ground proposal submitted successfully!"


@app.route('/organization_requests')
def organization_requests():
    # Fetch ground proposals from MongoDB
    oproposals = list(oproposals_collection.find())
    return render_template('organization_requests.html', oproposals=oproposals)
"""ORGANIZATION END"""

"""EVENT REG"""
@app.route('/event_register', methods=['GET', 'POST'])
def event_register():
    if request.method == 'POST':
        # Process form submission
        event_name = request.form['event_name']
        user_name = request.form['user_name']
        email = request.form['email']
        contact_number = request.form['contact_number']

        # Store the registration data in session
        session['registration_data'] = {
            'event_name': event_name,
            'user_name': user_name,
            'email': email,
            'contact_number': contact_number
        }

        return redirect(url_for('transaction'))

    # Fetch active events from MongoDB for dropdown
    active_events = events_collection.find({'status': 'Active'}, {'event_name': 1})

    # Convert cursor to list for easier iteration in template
    events = list(active_events)

    return render_template('student/event_register.html', events=events)

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if request.method == 'POST':
        # Simulate payment success (for demo purposes)
        payment_successful = True

        if payment_successful:
            # Retrieve registration data from session
            registration_data = session.pop('registration_data', None)

            if registration_data:
                # Store registration details in MongoDB
                registration_id = registrations_collection.insert_one(registration_data).inserted_id

                # Generate invoice
                invoice_data = {
                    'registration_id': registration_id,
                    'event_name': registration_data['event_name'],
                    'user_name': registration_data['user_name'],
                    'email': registration_data['email'],
                    'contact_number': registration_data['contact_number'],
                    'payment_status': 'Success',
                    'payment_date': datetime.now()
                }

                # Store invoice details in MongoDB
                invoice_id = invoices_collection.insert_one(invoice_data).inserted_id

                flash('Payment done and registration successful.', 'success')
                flash(f'Invoice generated with ID: {invoice_id}', 'info')
            else:
                flash('Error processing registration. Please try again.', 'error')
        else:
            flash('Payment failed. Please try again.', 'error')

        return redirect(url_for('event_register'))

    return render_template('student/transaction.html')


@app.route('/registrations')
def registrations():
    # Fetch registration details from MongoDB
    registrations = list(registrations_collection.find())
    return render_template('eventorganizer/registrations.html', registrations=registrations)

@app.route('/invoices')
def invoices():
    # Fetch invoice details from MongoDB
    invoices = list(invoices_collection.find())
    return render_template('student/invoices.html', invoices=invoices)


# @app.route('/download_receipt/<invoice_id>')
# def download_receipt(invoice_id):
#     # Fetch invoice details from MongoDB based on invoice_id
#     invoice = invoices_collection.find_one({'_id': ObjectId(invoice_id)})
    
#     if invoice:
#         # Render the HTML template with invoice data
#         html = render_template_string('student/receipt_template.html', invoice=invoice)
        
#         # Generate PDF from HTML using weasyprint
#         pdf_file = tempfile.NamedTemporaryFile(delete=False)
#         HTML(string=html).write_pdf(pdf_file)
        
#         # Create response object
#         with open(pdf_file.name, 'rb') as file:
#             pdf_data = file.read()
        
#         response = make_response(pdf_data)
#         response.headers['Content-Type'] = 'application/pdf'
#         response.headers['Content-Disposition'] = f'inline; filename=invoice_{invoice_id}.pdf'
        
#         # Delete temporary files
#         pdf_file.close()
        
#         return response
#     else:
#         flash('Invoice not found.', 'error')
#         return redirect(url_for('invoices'))

"""EVENT REG END"""


@app.route('/event_logout')
def event_logout():
    session.pop('username', None)  
    return redirect(url_for('main_screen'))  

"""ORGANIER LOGIN END"""

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
