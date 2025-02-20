# Importing the Flask Framework

import re
from flask import *
from database import * 
from aircrafts import *
from math import *

import database
import configparser


# appsetup

page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
dbuser = config['DATABASE']['user']
portchoice = config['FLASK']['port']
if portchoice == '10000':
    print('ERROR: Please change config.ini as in the comments or Lab instructions')
    exit(0)

session['isadmin'] = False

###########################################################################################
###########################################################################################
####                                 Database operative routes                         ####
###########################################################################################
###########################################################################################



#####################################################
##  INDEX
#####################################################

# What happens when we go to our website (home page)
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['username'] = dbuser
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

#####################################################
# User Login related                        
#####################################################
# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'dbuser' : dbuser}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['userid'], request.form['password'])
        print(val)
        print(request.form)
        # If our database connection gave back an error
        if(val == None):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))

        # If it was successful, then we can log them in :)
        print(val[0])
        session['name'] = val[0]['firstname']
        session['userid'] = request.form['userid']
        session['logged_in'] = True
        session['isadmin'] = val[0]['isadmin']
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)

# logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))



########################
#List All Items#
########################

@app.route('/users')
def list_users():
    '''
    List all rows in users by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_listdict = database.list_users()

    # Handle the null condition
    if (users_listdict is None):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users')
    page['title'] = 'List Contents of users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)
    

########################
#List Single Items#
########################


@app.route('/users/<userid>')
def list_single_users(userid):
    '''
    List all rows in users that match a particular id attribute userid by calling the 
    relevant database calls and pushing to the appropriate template
    '''

    # connect to the database and call the relevant function
    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)
    page['title'] = 'List Single userid for users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)


########################
#List Search Items#
########################

@app.route('/consolidated/users')
def list_consolidated_users():
    '''
    List all rows in users join userroles 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_userroles_listdict = database.list_consolidated_users()

    # Handle the null condition
    if (users_userroles_listdict is None):
        # Create an empty list and show error message
        users_userroles_listdict = []
        flash('Error, there are no rows in users_userroles_listdict')
    page['title'] = 'List Contents of Users join Userroles'
    return render_template('list_consolidated_users.html', page=page, session=session, users=users_userroles_listdict)

@app.route('/user_stats')
def list_user_stats():
    '''
    List some user stats
    '''
    # connect to the database and call the relevant function
    user_stats = database.list_user_stats()

    # Handle the null condition
    if (user_stats is None):
        # Create an empty list and show error message
        user_stats = []
        flash('Error, there are no rows in user_stats')
    page['title'] = 'User Stats'
    return render_template('list_user_stats.html', page=page, session=session, users=user_stats)

@app.route('/users/search', methods=['POST', 'GET'])
def search_users_byname():
    '''
    List all rows in users that match a particular name
    by calling the relevant database calls and pushing to the appropriate template
    '''
    if(request.method == 'POST'):

        search = database.search_users_customfilter(request.form['searchfield'],"~",request.form['searchterm'])
        print(search)
        
        users_listdict = None

        if search == None:
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('index'))
        if search == None or len(search) < 1:
            flash(f"No items found for search: {request.form['searchfield']}, {request.form['searchterm']}")
            return redirect(url_for('index'))
        else:
            
            users_listdict = search
            # Handle the null condition'
            print(users_listdict)
            if (users_listdict is None or len(users_listdict) == 0):
                # Create an empty list and show error message
                users_listdict = []
                flash('Error, there are no rows in users that match the searchterm '+request.form['searchterm'])
            page['title'] = 'Users search by name'
            return render_template('list_users.html', page=page, session=session, users=users_listdict)
            

    else:
        return render_template('search_users.html', page=page, session=session)
        
@app.route('/users/delete/<userid>')
def delete_user(userid):
    '''
    Delete a user
    '''
    # connect to the database and call the relevant function
    resultval = database.delete_user(userid)
    
    page['title'] = f'List users after user {userid} has been deleted'
    return redirect(url_for('list_consolidated_users'))
    
@app.route('/users/update', methods=['POST','GET'])
def update_user():
    """
    Update details for a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update user details'

    userslist = None

    print("request form is:")
    newdict = {}
    print(request.form)

    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        return redirect(url_for('list_consolidated_users'))

######
## Edit user
######
@app.route('/users/edit/<userid>', methods=['POST','GET'])
def edit_user(userid):
    """
    Edit a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Edit user details'

    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    user = users_listdict[0]
    validupdate = False

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        # assuming GET request, need to setup for this
        return render_template('edit_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles(),
                           user=user)


######
## add items
######

    
@app.route('/users/add', methods=['POST','GET'])
def add_user():
    """
    Add a new User
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Add user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that all values are available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not add user without a userid")
            return redirect(url_for('add_user'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = 'Empty firstname'
        else:
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = 'Empty lastname'
        else:
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = 1 # default is traveler
        else:
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = 'blank'
        else:
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Insert parametesrs are:')
        print(newdict)

        database.add_user_insert(newdict['userid'], newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        # Should redirect to your newly updated user
        print("did it go wrong here?")
        return redirect(url_for('list_consolidated_users'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles())

#########################################################################################################################################################

'''
Extract relevant data from the form (page) for aircrafts
Returns 
    - a dictionary of updated values
    - boolean indicating if any updates were made
'''
def extract_aircraft_data(form):
    update_data = {
        'AircraftID': form.get('AircraftID'),
        'ICAOCode': form.get('icao_code'),
        'AircraftRegistration': form.get('aircraft_registration'),
        'Manufacturer': form.get('manufacturer'),
        'Model': form.get('model'),
        'Capacity': form.get('capacity')
    }
    valid_update = any(value for value in update_data.values() if value)  
    return update_data, valid_update

def extract_aircraft_data_add(form):
    update_data = {
        'AircraftID': form.get('aircraft_id'),  
        'ICAOCode': form.get('icao_code'),
        'AircraftRegistration': form.get('aircraft_registration'),
        'Manufacturer': form.get('manufacturer'),
        'Model': form.get('model'),
        'Capacity': form.get('capacity')
    }
    valid_update = any(value for value in update_data.values() if value)  
    return update_data, valid_update

'''
Delete an aircraft from the database
Return   
    - redirects back to the aircraft list with message after deletion
'''
@app.route('/aircrafts/delete/<aircraft_id>', methods=['POST'])
def delete_aircraft(aircraft_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    remove_aircraft(aircraft_id)
    flash(f'Aircraft {aircraft_id} has been successfully deleted.')
    return redirect(url_for('list_aircrafts'))

'''
Add a new aircraft to the database
Return
    - a form to add new aircraft and handles submissions
'''
@app.route('/add_aircraft', methods=['GET', 'POST'])
def add_aircraft_route():
    if request.method == 'POST':
        print("Form data received:", request.form) 

        aircraft_id = request.form.get('aircraft_id', '').strip()
        icao_code = request.form.get('icao_code', '').strip()
        aircraft_registration = request.form.get('aircraft_registration', '').strip()
        manufacturer = request.form.get('manufacturer', '').strip()
        model = request.form.get('model', '').strip()
        capacity = request.form.get('capacity', '').strip()

        #check all fields are entered
        if not aircraft_id:
            flash("Error: Aircraft ID is required.", "error")
            return redirect(url_for('add_aircraft_route'))
        
        if not icao_code:
            flash("Error: ICAO code is required.", "error")
            return redirect(url_for('add_aircraft_route'))
        
        if not aircraft_registration:
            flash("Error: Aircraft registration is required.", "error")
            return redirect(url_for('add_aircraft_route'))

        if not manufacturer:
            flash("Error: Manufacturer is required.", "error")
            return redirect(url_for('add_aircraft_route'))

        if not model:
            flash("Error: Model is required.", "error")
            return redirect(url_for('add_aircraft_route'))

        if not capacity:
            flash("Error: Capacity is required.", "error")
            return redirect(url_for('add_aircraft_route'))

        #check id is integer
        try:
            aircraft_id_value = int(aircraft_id)
        except ValueError:
            flash("Error: Aircraft ID must be an integer.", "error")
            print("not an integer")
            return redirect(url_for('add_aircraft_route'))
        
        #check icao code
        if icao_code and len(icao_code) != 4:
            flash("Error: ICAO code must be exactly 4 characters.", "error")
            return redirect(url_for('add_aircraft_route'))
        
        #check aircraft registration
        if aircraft_registration and not re.match(r'^[A-Za-z0-9]{2}-[A-Za-z0-9]{3}$', aircraft_registration):
            flash("Error: Aircraft registration must be in the format ##-### (letters or numbers).", "error")
            return redirect(url_for('add_aircraft_route'))
        
        #check capacity
        try:
            capacity_value = int(capacity)
            if capacity_value < 0:
                flash("Error: Capacity cannot be negative.", "error")
                return redirect(url_for('add_aircraft_route'))
        except ValueError:
            flash("Error: Capacity must be a valid number.", "error")
            return redirect(url_for('add_aircraft_route'))
        
        #check aircraft ID exists
        if (aircraft_exists(aircraft_id)):
            flash("Error: Aircraft ID already exists.", "error")
            return redirect(url_for('add_aircraft_route'))

        
        aircraft_data, _ = extract_aircraft_data_add(request.form)
        
        add_aircraft(
            aircraft_data['AircraftID'],
            aircraft_data.get('ICAOCode'),
            aircraft_data.get('AircraftRegistration'),
            aircraft_data.get('Manufacturer'),
            aircraft_data.get('Model'),
            aircraft_data.get('Capacity')
        )
        
        return redirect(url_for('add_aircraft_route'))
    
    return render_template('add_aircraft.html', page={'title': 'Add Aircraft'})


'''
Edit an existing aircraft's details 
Return 
    - a form for updating fields 
'''
@app.route('/modify_aircraft', methods=['GET', 'POST'])
@app.route('/aircrafts/edit/<aircraft_id>', methods=['GET', 'POST'])
def modify_aircraft_route(aircraft_id=None):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    page_title = 'Modify Aircraft'
    aircraft_details = {}

    if aircraft_id:
        page_title = 'Edit Aircraft Details'
        aircraft_details = get_aircraft_by_id(aircraft_id)
        if aircraft_details is None:
            flash(f'Error: No aircraft found with ID {aircraft_id}')
            return redirect(url_for('list_aircrafts'))
    
    icao_code = request.form.get('icao_code', '').strip()
    if icao_code and len(icao_code) != 4:
        flash("Error: ICAO code must be exactly 4 characters.", "error")
        return redirect(url_for('modify_aircraft_route', aircraft_id=aircraft_id))

    if request.method == 'POST':
        if 'AircraftID' not in request.form:
            flash('Error: Aircraft ID is required.')
            return redirect(url_for('list_aircrafts'))
        
        #check icao code (exactly 4 characters)
        icao_code = request.form.get('icao_code', '').strip()
        if icao_code and len(icao_code) != 4:
            flash("Error: ICAO code must be exactly 4 characters.", "error")
            return redirect(url_for('modify_aircraft_route', aircraft_id=aircraft_id))

        #check regristration in the form ##-###
        aircraft_registration = request.form.get('aircraft_registration', '').strip()
        if aircraft_registration and not re.match(r'^[A-Za-z0-9]{2}-[A-Za-z0-9]{3}$', aircraft_registration):
            flash("Error: Aircraft registration must be in the format ##-### (letters or numbers).", "error")
            return redirect(url_for('modify_aircraft_route', aircraft_id=aircraft_id))
        
        #check capacity not negative 
        capacity = request.form.get('capacity', '').strip()
        try:
            capacity_value = int(capacity)
            if capacity_value < 0:
                flash("Error: Capacity cannot be negative.", "error")
                return redirect(url_for('modify_aircraft_route', aircraft_id=aircraft_id))
        except ValueError:
            flash("Error: Capacity must be a valid number.", "error")
            return redirect(url_for('modify_aircraft_route', aircraft_id=aircraft_id))
        
        update_data, valid_update = extract_aircraft_data(request.form)

        if valid_update:
            modify_aircraft(
                update_data['AircraftID'],
                update_data.get('ICAOCode'),
                update_data.get('AircraftRegistration'),
                update_data.get('Manufacturer'),
                update_data.get('Model'),
                update_data.get('Capacity')
            )
            flash(f'Aircraft {update_data["AircraftID"]} updated successfully.')
            return redirect(url_for('list_aircrafts_route')) 
        else:
            flash("No updated values for aircraft.")
            return redirect(url_for('modify_aircraft', aircraft_id=aircraft_id))

    current_page = 'modify_aircraft' 
    return render_template(
        'modify_aircraft.html',
        session=session,
        page={'title': page_title, 'current_page': current_page},  
        aircraft=aircraft_details 
    )


'''
Remove an aircraft from the database
'''
@app.route('/remove_aircraft/<aircraft_id>', methods=['GET', 'POST'])
@app.route('/remove_aircraft', methods=['GET', 'POST'])
def remove_aircraft_route():
    if request.method == 'POST':
        aircraft_id = request.form['aircraft_id'] 
        remove_aircraft(aircraft_id)
        flash(f'Aircraft {aircraft_id} has been successfully deleted.')
        return redirect(url_for('list_aircrafts_route')) 
    return render_template('remove_aircraft.html', page={'title': 'Remove Aircraft'})


'''
List all unique aircraft manufacturers from the database
Return
    - a page showing the distinct manufacturers
'''
@app.route('/list_manufacturers')
def list_manufacturers_route():
    manufacturers = get_unique_manufacturers()
    return render_template('list_manufacturers.html', manufacturers=manufacturers, page={'title': 'List Manufacturers'})

'''
Count the number of aircrafts by each manufacturer
Return
    - a list of manufacturers and the number of aircraft each one has
'''
@app.route('/count_aircraft')
def count_aircraft_route():
    counts = get_aircraft_count_by_manufacturer()
    return render_template('count_aircraft.html', counts=counts, page={'title': 'Count Aircraft by Manufacturer'})

'''
List all aircraft currently in the database
Return 
    - a list of aircraft with sorting options for fields
'''
@app.route('/list_aircrafts')
def list_aircrafts_route():
    page = request.args.get('page', 1, type=int)
    per_page = 5 

    sort = request.args.get('sort', 'aircraftid')  #default sort by Aircraft ID asc
    order = request.args.get('order', 'asc')  

    total_aircrafts = list_aircrafts()

    if order == 'asc':
        total_aircrafts.sort(key=lambda x: x.get(sort, ''))
    else:
        total_aircrafts.sort(key=lambda x: x.get(sort, ''), reverse=True)
        
    total_pages = (len(total_aircrafts) + per_page - 1) // per_page 

    start = (page - 1) * per_page
    end = start + per_page
    aircraft_list = total_aircrafts[start:end]

    return render_template('list_aircrafts.html',
                           page={'title': 'List of Aircraft', 'current_page': page, 'total_pages': total_pages},
                           session=session,
                           aircrafts=aircraft_list)

'''
Search for an aircraft by all fields 
Return
    - Filtered aircrafts 
'''
@app.route('/search_aircraft', methods=['GET'])
def search_aircraft_route():
    query = request.args.get('query', '').strip().lower()

    aircrafts = list_aircrafts() 

    filtered_aircrafts = [
        aircraft for aircraft in aircrafts if (
            query in str(aircraft['aircraftid']).lower() or
            query in aircraft['icaocode'].lower() or
            query in aircraft['aircraftregistration'].lower() or
            query in aircraft['manufacturer'].lower() or
            query in aircraft['model'].lower() or
            query in str(aircraft['capacity']).lower()
        )
    ]

    return render_template('list_aircrafts.html',
                           page={'title': 'Search Results', 'current_page': 1, 'total_pages': 1},
                           session=session,
                           aircrafts=filtered_aircrafts)


'''
Display the details of a single aircraft
Return 
    - details of a specific aircraft by ID 
'''
@app.route('/aircraft/<aircraft_id>')
def list_single_aircraft(aircraft_id):
    aircraft_details = get_aircraft_by_id(aircraft_id)
    if not aircraft_details:
        flash(f'Error: No aircraft found with ID {aircraft_id}')
        return redirect(url_for('list_aircrafts'))

    return render_template('list_aircrafts.html', aircraft=aircraft_details, page={'title': f'Aircraft {aircraft_id} Details'})
