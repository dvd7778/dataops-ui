import streamlit as st
import pandas as pd
import requests
from streamlit_option_menu import option_menu
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import locale
import datetime


# Initialize session state for login status
st.set_page_config(
    page_title='Hotel Analytical System',
    page_icon='🏨',
    layout='wide',
    initial_sidebar_state='collapsed',
    menu_items={
        'Report a bug': 'mailto:jean.pagan5@upr.edu',
        'About': """ Hotel Analytical System v1.0
        
Created by DataOps:

- David Castillo Martinez (david.castillo1@upr.edu)
- Jean C. Pagan Vega (jean.pagan5@upr.edu)
- Jan Nieves Soto (jan.nieves3@upr.edu)
- Diego Aviles Cordero (diego.aviles1@upr.edu)

Class: ICOM5016
"""}
)

url = "https://database-phase1-dataops-74deb9d967c0.herokuapp.com"


if 'user' not in st.session_state:
    st.session_state['user'] = None
    st.session_state['password'] = None
    st.session_state['eid'] = None
    st.session_state['login'] = False
    st.session_state['logout'] = False
    st.session_state['first_time'] = True
    st.session_state['position'] = None
    locale.setlocale(locale.LC_ALL, '')
left_column, right_column = st.columns(2)

def is_float(string):
    try:
        num = float(string)
        if num >= 0:
            return True
        else:
            return False
    except ValueError:
        return False

def is_int(string):
    try:
        num = int(string)
        if num >= 0:
            return True
        else:
            return False
    except ValueError:
        return False


def main():
    if not st.session_state['user'] and st.session_state['first_time']:
        menu = ["Home", "Login", "Create Employee Account"]
        choice = st.sidebar.selectbox("Menu", menu)
        st.session_state['first_time'] = False
    elif not st.session_state['user'] and not st.session_state['first_time']:
        menu = ["Home", "Login", "Create Employee Account"]
        choice = st.sidebar.selectbox("Menu", menu, index=1)
    else:
        menu = ["Home", "Logout", "Statistics", "Manage Entities"]
        choice = st.sidebar.selectbox("Menu", menu, index=2)
        
    global_administrator = ["Top 3 chains with the highest total revenue.", 
                            "Total reservation percentage by payment method.",
                            "Top 3 hotel chains with the least rooms.",
                            "Top 5 hotels with the most client capacity.",
                            "Top 10% of the hotels that had the most reservations.",
                            "Top 3 month with the most reservation by chain."
                            ]
    local_administrator = ["Top 5 handicap rooms that were reserved the most.",
                            "Top 3 rooms that were the least time unavailable.",
                            "Top 5 clients under 30 years old that made the most reservation with a credit card.",
                            "Top 3 highest paid regular employees.",
                            "Top 5 clients that received the most discounts.", 
                            "Total reservation percentage by room type.",
                            "Top 3 rooms that were reserved that had the least guest-to-capacity ratio."]
    if st.session_state["position"] == "Administrator":
        create_entities = ["Login", "Employee", "Chain", "Hotel", "Room Description", "Client", "Reserve", "Room", "Room Unavailable"]
    elif st.session_state["position"] == "Supervisor":
        create_entities = ["Room Unavailable"]
    else:
        create_entities = ["Reserve"]

    entity_endpoints = {
                "Login": ("/dataops/login", "lid"),
                "Employee": ("/dataops/employee", "eid"),
                "Chain": ("/dataops/chains", "chid"),
                "Hotel": ("/dataops/hotel", "hid"),
                "Room Description": ("/dataops/roomdescription", "rdid"),
                "Client": ("/dataops/client", "clid"),
                "Reserve": ("/dataops/reserve", "reid"),
                "Room": ("/dataops/room", "rid"),
                "Room Unavailable": ("/dataops/roomunavailable", "ruid"),
            }
    
    fade_in_style = """
        <style>
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        .fade-in {
            animation: fadeIn 2s ease-in-out;
        }
        </style>
        """
        
    st.markdown(fade_in_style, unsafe_allow_html=True)

    if choice == "Home":
        st.image('Hotel_Analytical_System_1.png', use_column_width=True)
        st.markdown('<h2 class="fade-in">Welcome to our Hotel Analytical System!🏨</h2>', unsafe_allow_html=True)
        if st.session_state['user']:
            st.success('You are currently logged in.')
        else:
            st.warning('Please log in using the sidebar.')

        col1, col2 = st.columns([3, 1])  # Split page into two columns, ratio 3:1

    # List of hotel photo paths
        hotel_photos = ['Chain1.png', 'Chain2.png', 'Chain3.png', 'Chain4.png', 'Chain5.png']

    # Display hotel photos in the right column
        with col2:
            st.write("<h3 class='fade-in'>Our Biggest Users:</h3>", unsafe_allow_html=True)
            for photo in hotel_photos:
                st.image(photo, width=200, caption='')

        about_text = """
    <div class="fade-in">
        <strong>About:</strong>
    
    Our Hotel Analytical System is designed to streamline the process of managing hotel reservations, providing hotel staff with a user-friendly interface for handling bookings, accessing statistics, and performing administrative tasks.
      
      ***Key Features:***
          
    - **Login Page:** 🔐 
      - Easily login or create an employee account to access the system's features.

    - **Local Statistics:** 📊  
      - Access statistics related to hotel operations.

    - **Global Statistics:** 📊
      - Exclusive access for high-ranking employees to view comprehensive global statistics.

    - **Web-Based Dashboard:** 📊
      - Access valuable statistics and insights through our user-friendly web-based dashboard, enhancing your reservation management experience.

    - **Create:** ✏️ 
      - Create and manage records in the system.
      
    - **Update & Delete:** ✅❌ 
      - Users with authorization can update or delete records in the database, ensuring data accuracy and integrity.

    Experience the ease and efficiency of hotel reservation management with our intuitive solution!
    </div>
    """
        with col1:
            st.markdown(about_text, unsafe_allow_html=True)
            
            st.markdown("<h3 class='fade-in'>How to Use:</h3>", unsafe_allow_html=True)
            st.write("""
            - **Step 1:** Log in using the sidebar if you haven't already.
            - **Step 2:** Navigate to the desired feature using the sidebar menu.
            - **Step 3:** Follow the on-screen instructions to perform actions such as creating reservations, viewing statistics, and managing records.
            - **Step 4:** Enjoy the efficiency and convenience of our Hotel Reservation Management System!
            """)
            
#-------------------------------------------------------CREATE NEW ENTITIES-------------------------------------------------------------   
    elif choice == "Manage Entities":
        if st.session_state["position"] == "Administrator":            
            crud_choice = option_menu(
                    menu_title = None,
                    options = ["Create", "Update", "Delete"],
                    icons= ["pencil-square", "arrow-clockwise", "trash"],
                    orientation= "horizontal",
                    styles={"nav-link-selected": {"background-color": "SlateGrey"},"nav-link": {"font-size": "25px", "margin":"0px", "--hover-color": "LightGray"},}
                    )
        else:
            crud_choice = option_menu(
                    menu_title = None,
                    options = ["Create"],
                    icons= ["pencil-square"],
                    orientation= "horizontal",
                    styles={"nav-link-selected": {"background-color": "SlateGrey"},"nav-link": {"font-size": "25px", "margin":"0px", "--hover-color": "LightGray"},}
                    )
        st.sidebar.success("Logged in as " + st.session_state["position"])
        
        if crud_choice == "Create":
            selected_entity = st.selectbox("Select Entity to Create", create_entities, index=None)
            if selected_entity == "Login":
                st.header("")
                employee_ids = requests.get(url + "/dataops/employee").json()
                employee_ids = [employee["eid"] for employee in employee_ids if employee["eid"] != -1]
                eid = st.selectbox("Enter Employee ID", employee_ids, index=None)
                usernamelogin = st.text_input("Enter Username")
                passwordlogin = st.text_input("Password", type='password')
                
                if st.button("Create", use_container_width=True):
                    if usernamelogin and passwordlogin and eid:
                        account = requests.get(url + "/dataops/login/byemployeeid/" + str(eid)).json()
                        data = requests.get(url + "/dataops/login/byusername",
                            params = {
                                "username" : usernamelogin
                                }
                            ).json()
                        if account != "Not Found":
                            st.warning("There is already an account for this Employee ID")
                        elif data != "Not Found":
                            st.warning("This username is already taken")
                        else:
                            requests.post(url + "/dataops/login", json={"eid" : int(eid), "username" : usernamelogin, "password" : passwordlogin}).json()
                            st.success("Account was created successfully")
                    else:
                        st.warning("Please fill all the fields above")

            if selected_entity == "Employee":
                st.header("")
                hotel_ids = requests.get(url + "/dataops/hotel").json()
                hotel_ids = [str(hotel["hid"]) for hotel in hotel_ids if hotel["hid"] != -1]
                hid = st.selectbox("Enter Hotel ID", hotel_ids, index=None)
                fname = st.text_input("Enter First Name")
                lname = st.text_input("Enter Last Name")
                age = st.text_input("Enter Age")
                position = st.radio("Choose a Position", {"Administrator","Regular","Supervisor"}, index=None)
                salary = st.text_input("Enter Salary")
                
                if st.button("Create", use_container_width=True):
                    if hid and fname and lname and age and position and salary:
                        if is_int(age) and is_float(salary):
                            requests.post(url + "/dataops/employee", json={"hid" : int(hid), "fname" : fname, "lname" : lname, "age" : int(age), "position" : position, "salary" : float(salary)}).json()
                            st.success("Employee was created successfully")
                        else:
                            st.warning("The age must be a positive whole number and the salary must be a numerical value")
                    else:
                        st.warning("Please fill all the above fields")

            if selected_entity == "Chain":
                st.header("")
                cname = st.text_input("Enter Chain Name")
                springmkup = st.text_input("Enter Spring Markup Amount")
                summermkup = st.text_input("Enter Summer Markup Amount")
                wintermkup = st.text_input("Enter Winter Markup Amount")
                fallmkup = st.text_input("Enter Fall Markup Amount")
                
                if st.button("Create", use_container_width=True):
                    if cname and springmkup and summermkup and wintermkup and fallmkup:
                        if is_float(springmkup) and is_float(summermkup) and is_float(wintermkup) and is_float(fallmkup):
                            requests.post(url + "/dataops/chains", json={"cname" : cname, "springmkup" : float(springmkup), "summermkup" : float(summermkup), "wintermkup" : float(wintermkup), "fallmkup" : float(fallmkup)}).json()
                            st.success("Chain was created successfully")
                        else:
                            st.warning("The spring, summer, fall and winter markups must be numerical values")
                    else:
                        st.warning("Please fill all the fields above")

            if selected_entity == "Hotel":
                st.header("")
                chain_ids = requests.get(url + "/dataops/chains").json()
                chain_ids = [str(chain["chid"]) for chain in chain_ids if chain["chid"] != -1]
                chid = st.selectbox("Enter Chain ID", chain_ids, index=None)
                hname = st.text_input("Enter Hotel Name")
                hcity = st.text_input("Enter Hotel City")
                
                if st.button("Create", use_container_width=True):
                    if chid and hname and hcity:
                        requests.post(url + "/dataops/hotel", json={"chid" : chid, "hname" : hname, "hcity" : hcity}).json()
                        st.success("Hotel was created successfully")
                    else:
                        st.warning("Please fill all the fields above")

            if selected_entity == "Room Description":
                st.header("")
                room_constraints = {
                    "Standard": {"capacity": {1}, "types": {"Basic", "Premium"}},
                    "Standard Queen": {"capacity": {1, 2}, "types": {"Basic", "Premium", "Deluxe"}},
                    "Standard King": {"capacity": {2}, "types": {"Basic", "Premium", "Deluxe"}},
                    "Double Queen": {"capacity": {4}, "types": {"Basic", "Premium", "Deluxe"}},
                    "Double King": {"capacity": {4, 6}, "types": {"Basic", "Premium", "Deluxe", "Suite"}},
                    "Triple King": {"capacity": {6}, "types": {"Deluxe", "Suite"}},
                    "Executive Family": {"capacity": {4, 6, 8}, "types": {"Deluxe", "Suite"}},
                    "Presidential": {"capacity": {4, 6, 8}, "types": {"Suite"}}
                }
                rname = st.radio("Choose Room Name", list(room_constraints.keys()))
                constraints = room_constraints.get(rname, {"capacity": set(), "types": set()})
                rtype = st.radio("Choose Room Type", constraints["types"])
                capacity = st.radio("Choose Capacity Of Guests", constraints["capacity"])
                ishandicap = st.radio("Choose Handicapped Accessibility", {False, True})
                
                if st.button("Create", use_container_width=True):
                    requests.post(url + "/dataops/roomdescription", json={"rname" : rname, "rtype" : rtype, "capacity" : capacity, "ishandicap" : ishandicap}).json()
                    st.success("Room description was created successfully")
                    
            if selected_entity == "Client":
                st.header("")
                fname = st.text_input("Enter First Name")
                lname = st.text_input("Enter Last Name")
                age = st.text_input("Enter Employee Age")
                memberyear = st.text_input("Enter Member Year Amount")
                
                if st.button("Create", use_container_width=True):
                    if fname and lname and age and memberyear:
                        if is_int(age) and is_int(memberyear):
                                requests.post(url + "/dataops/client", json={"fname" : fname, "lname" : lname, "age" : int(age), "memberyear" : int(memberyear)}).json()
                                st.success("Client was created successfully")
                        else:
                                st.warning("The age and member year must be integer values")
                    else:
                        st.warning("Please fill all the fields above")

            if selected_entity == "Reserve":
                st.header("")
                methods = ["cash", "check", "credit card", "debit card", "pear pay"]
                clients = requests.get(url + "/dataops/client").json()
                roomsunavailable = requests.get(url + "/dataops/roomunavailable").json()
                roomunavailable_ids = [str(room["ruid"]) for room in roomsunavailable if room["ruid"] != -1]
                client_ids = [str(client["clid"]) for client in clients if client["clid"] != -1]
                ruid = st.selectbox("Enter Unavailable Room ID", roomunavailable_ids, index=None)
                clid = st.selectbox("Enter Client ID", client_ids, index=None)
                payment = st.selectbox("Enter Payment Method", methods, index=None)
                guests = st.text_input("Enter Reservation Guests")
                
                if st.button("Create", use_container_width=True):
                    if ruid and clid and payment and guests:
                        if is_int(guests):
                            total_cost = requests.get(url + "/dataops/reserve/totalcost/" + str(ruid) + "/" + str(clid)).json()
                            if not total_cost:
                                st.warning("There is already a reservation with the selected Client ID and the selected Room Unavailable ID")
                            else:
                                requests.post(url + "/dataops/reserve", json={"ruid" : ruid, "clid" : clid, "total_cost" : float(total_cost[0]["Total Cost"]), "payment" : payment, "guests" : guests}).json()
                                st.success("Reservation was created successfully")
                        else:
                            st.warning("The amount of guests must be a positive whole number")
                    else:
                        st.warning("Please fill all the fields above")
                        

            if selected_entity == "Room":
                st.header("")
                hotel_ids = requests.get(url + "/dataops/hotel").json()
                hotel_ids = [str(hotel["hid"]) for hotel in hotel_ids if hotel["hid"] != -1]
                roomdescription_ids = requests.get(url + "/dataops/roomdescription").json()
                roomdescription_ids = [str(roomdescription["rdid"]) for roomdescription in roomdescription_ids if roomdescription["rdid"] != -1]
                hid = st.selectbox("Enter Hotel ID", hotel_ids, index=None)
                rdid = st.selectbox("Enter Room Description ID", roomdescription_ids, index=None)
                rprice = st.text_input("Enter Room Price")
                
                if st.button("Create", use_container_width=True):
                    if hid and rdid and rprice:
                        if is_float(rprice):
                            requests.post(url + "/dataops/room", json={"hid" : hid, "rdid" : rdid, "rprice" : float(rprice)}).json()
                            st.success("Room was created successfully")
                        else:
                            st.warning("The price must be a numerical value")
                    else:
                        st.warning("Please fill all the fields above")

            if selected_entity == "Room Unavailable":
                st.header("")
                room_ids = requests.get(url + "/dataops/room").json()
                room_ids = [str(room["rid"]) for room in room_ids if room["rid"] != -1]
                rid = st.selectbox("Enter Room ID", room_ids, index=None)
                dates = st.date_input("Enter the Reservation's Start and End Date", value=(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=1)))   
                
                if st.button("Create", use_container_width=True):   
                    if rid:        
                        if len(dates) < 2:
                            st.warning("Please select a start and end date for the reservation")
                        else:
                            startdate = dates[0]
                            enddate = dates[1]
                            requests.post(url + "/dataops/roomunavailable", json={"rid" : rid, "startdate" : str(startdate), "enddate" : str(enddate)}).json()
                            st.success("Room Unavailable was created successfully")
                    else:
                        st.warning("Please fill all the fields above")
                                
        elif crud_choice == "Update":
            selected_entity = st.selectbox("Select Entity to Update", create_entities, index=None)
            
            if selected_entity == "Login":
                st.header("")
                logins = requests.get(url + "/dataops/login").json()
                login_ids = [str(login["lid"]) for login in logins if login["lid"] != -1]
                lid = st.selectbox("Enter Login ID", login_ids, index=None)
                if lid:
                    selected_login = requests.get(url + "/dataops/login/" + lid).json()
                    employees = requests.get(url + "/dataops/employee").json()
                    employee_ids = [str(employee["eid"]) for employee in employees if employee["eid"] != -1]
                    curr_username = selected_login["username"]
                    curr_password = selected_login["password"]
                    curr_eid = selected_login["eid"]
                    eid = st.selectbox("Enter the new Employee ID", employee_ids, index=None)
                    username = st.text_input("Enter the new Username", value=curr_username)
                    password = st.text_input("Enter the new Password", value=curr_password, type='password')
                    
                    if st.button("Update", use_container_width=True):
                        if lid and eid and username and password:
                            new_login_by_id = requests.get(url + "/dataops/login/byemployeeid/" + eid).json()
                            if (new_login_by_id != "Not Found" and new_login_by_id["eid"] == curr_eid) or new_login_by_id == "Not Found":
                                new_login_by_username = requests.get(url + "/dataops/login/byusername", 
                                                                    params = {
                                                                        "username" : username
                                                                    }).json()
                                if (new_login_by_username != "Not Found" and new_login_by_username["eid"] == curr_eid) or new_login_by_username == "Not Found":
                                    requests.put(url + "/dataops/login/" + lid, json={"lid" : lid, "eid" : eid, "username" : username, "password" : password}).json()
                                    st.success("The record was successfully updated")
                                else:
                                    st.warning("The selected Username is already being used")
                            else:
                                st.warning("The selected Employee ID is already being used")
                        else:
                            st.warning("Please fill all the fields above")
                                
            if selected_entity == "Employee":
                st.header("")
                employees = requests.get(url + "/dataops/employee").json()
                employee_ids = [str(employee["eid"]) for employee in employees if employee["eid"] != -1]
                eid = st.selectbox("Enter Employee ID", employee_ids, index=None)
                if eid:
                    selected_employee = requests.get(url + "/dataops/employee/" + eid).json()
                    hotels = requests.get(url + "/dataops/hotel").json()
                    hotel_ids = [str(hotel["hid"]) for hotel in hotels if hotel["hid"] != -1]
                    curr_hid = selected_employee["hid"]
                    curr_fname = selected_employee["fname"]
                    curr_lname = selected_employee["lname"]
                    curr_age = selected_employee["age"]
                    curr_position = selected_employee["position"]
                    curr_salary = selected_employee["salary"]
                    hid = st.selectbox("Enter the new Hotel ID", hotel_ids, index=None)
                    fname = st.text_input("Enter the new First Name", value=curr_fname)
                    lname = st.text_input("Enter the new Last Name", value=curr_lname)
                    age = st.text_input("Enter the new Age", value=curr_age)
                    if curr_position == "Regular":
                        idx = 1
                    elif curr_position == "Administrator":
                        idx = 0
                    else:
                        idx = 2
                    position = st.radio("Choose a Position", ["Administrator","Regular","Supervisor"], index=idx)
                    salary = st.text_input("Enter the new Salary", value=curr_salary)
                    if st.button("Update", use_container_width=True):
                        if hid and fname and lname and age and position and salary:
                            if is_float(salary) and is_int(age):
                                requests.put(url + "/dataops/employee/" + eid, json={"eid" : eid, "hid" : hid, "fname" : fname, "lname" : lname, "age" : age, "position" : position, "salary" : salary}).json()
                                st.success("The record was successfully updated")
                            else:
                                st.warning("The salary and age must be numerical values with the age being a positive whole number")
                        else:
                            st.warning("Please fill all the fields above")
                            
            if selected_entity == "Chain":
                st.header("")
                chains = requests.get(url + "/dataops/chains").json()
                chain_ids = [str(chain["chid"]) for chain in chains if chain["chid"] != -1]
                chid = st.selectbox("Enter Chain ID", chain_ids, index=None)
                if chid:
                    selected_chain = requests.get(url + "/dataops/chains/" + chid).json()
                    curr_cname = selected_chain["cname"]
                    curr_springmkup = selected_chain["springmkup"]
                    curr_summermkup = selected_chain["summermkup"]
                    curr_fallmkup = selected_chain["fallmkup"]
                    curr_wintermkup = selected_chain["wintermkup"]
                    cname = st.text_input("Enter the new Chain Name", value=curr_cname)
                    springmkup = st.text_input("Enter the new Spring Markup", value=curr_springmkup)
                    summermkup = st.text_input("Enter the new Summer Markup", value=curr_summermkup)
                    fallmkup = st.text_input("Enter the new Fall Markup", value=curr_fallmkup)
                    wintermkup = st.text_input("Enter the new Winter Markup", value=curr_wintermkup)
                    if st.button("Update", use_container_width=True):
                        if chid and cname and springmkup and summermkup and fallmkup and wintermkup:
                            if is_float(springmkup) and is_float(summermkup) and is_float(wintermkup) and is_float(fallmkup):
                                requests.put(url + "/dataops/chains/" + chid, json={"chid" : chid, "cname" : cname, "springmkup" : springmkup, "summermkup" : summermkup, "fallmkup" : fallmkup, "wintermkup" : wintermkup}).json()
                                st.success("The record was successfully updated")
                            else:
                                st.warning("The Spring, Summer, Fall and Winter Markups must be numerical values")
                        else:
                            st.warning("Please fill all the above fields")
            
            if selected_entity == "Reserve":
                st.header("")
                methods = ["cash", "check", "credit card", "debit card", "pear pay"]
                reserves = requests.get(url + "/dataops/reserve").json()
                reserve_ids = [str(reserve["reid"]) for reserve in reserves if reserve["reid"] != -1]
                reid = st.selectbox("Enter Reservation ID", reserve_ids, index=None)
                if reid:
                    selected_reserve = requests.get(url+"/dataops/reserve/" + reid).json()
                    clients = requests.get(url + "/dataops/client").json()
                    client_ids = [str(client["clid"]) for client in clients if client["clid"] != -1]
                    roomunavailables = requests.get(url + "/dataops/roomunavailable").json()
                    roomunavailable_ids = [str(roomunavailable["ruid"]) for roomunavailable in roomunavailables if roomunavailable ["ruid"] != -1]
                    curr_clid = selected_reserve["clid"]
                    curr_guests = selected_reserve["guests"]
                    curr_payment = selected_reserve["payment"]
                    curr_ruid = selected_reserve["ruid"]
                    
                    if curr_payment == "cash":
                        idx = 0
                    elif curr_payment == "check":
                        idx = 1
                    elif curr_payment == "credit card":
                        idx = 2
                    elif curr_payment == "debit card":
                        idx = 3
                    else:
                        idx = 4
                        
                    clid = st.selectbox("Enter the new Client ID", client_ids, index=None)
                    ruid = st.selectbox("Enter the new Room Unavailable ID", roomunavailable_ids, index=None)
                    guests = st.text_input("Enter the new amount of Guests", value = curr_guests)
                    payment = st.selectbox("Enter the new Payment Method", methods, index=idx)
                    if st.button("Update", use_container_width=True):
                        if reid and clid and ruid and guests and payment:
                            if is_int(guests):
                                total_cost = requests.get(url + "/dataops/reserve/totalcost/" + str(ruid) + "/" + str(clid) + "/" + str(reid)).json()
                                if not total_cost:
                                    st.warning("There is already a reservation with the selected Client ID and the selected Room Unavailable ID")
                                else:
                                    requests.put(url + "/dataops/reserve/" + str(reid), json={"reid" : reid, "ruid" : ruid, "clid" : clid, "total_cost" : float(total_cost[0]["Total Cost"]), "payment" : payment, "guests" : guests}).json()
                                    st.success("The record was successfully updated")
                            else:
                                st.warning("The amount of guests must be a positive whole number")
                        else:
                            st.warning("Please fill all the above fields")
                            
            if selected_entity == "Client":
                st.header("")
                clients = requests.get(url + "/dataops/client").json()
                client_ids = [str(client["clid"]) for client in clients if client ["clid"] != -1]
                clid = st.selectbox("Enter Client ID", client_ids, index=None)
                if clid:
                    selected_client = requests.get(url + "/dataops/client/" + clid).json()
                    curr_fname = selected_client["fname"]
                    curr_lname = selected_client["lname"]
                    curr_age = selected_client["age"]
                    curr_memberyear = selected_client["memberyear"]
                    fname = st.text_input("Enter the new First name", value = curr_fname)
                    lname = st.text_input("Enter the new Last Name", value = curr_lname)
                    age = st.text_input("Enter the new Age", value = curr_age)
                    memberyear = st.text_input("Enter the new Years of Membership", value = curr_memberyear)
                    if st.button("Update", use_container_width=True):
                        if clid and fname and lname and age and memberyear:
                            if is_int(age) and is_int(memberyear):
                                requests.put(url + "/dataops/client/" + str(clid), json={"clid" : clid, "fname" : fname, "lname" : lname, "age" : int(age), "memberyear" : int(memberyear)}).json()
                                st.success("The record was successfully updated")
                            else:
                                st.warning("The age and membership year must be positive whole numbers")
                        else:
                            st.warning("Please fill all the above fields")
            
            if selected_entity == "Room Unavailable":
                st.header("")
                roomunavailables = requests.get(url + "/dataops/roomunavailable").json()
                roomunavailable_ids = [str(roomunavailable["ruid"]) for roomunavailable in roomunavailables if roomunavailable["ruid"] != -1]
                ruid = st.selectbox("Enter Room Unavailable ID", roomunavailable_ids, index = None)
                if ruid:
                    selected_room_unavailable = requests.get(url + "/dataops/roomunavailable/" + ruid).json()
                    rooms = requests.get(url + "/dataops/room").json()
                    room_ids = [str(room["rid"]) for room in rooms if room["rid"] != -1]
                    curr_rid = selected_room_unavailable["rid"]
                    curr_startdate = selected_room_unavailable["startdate"]
                    curr_enddate = selected_room_unavailable["enddate"]
                    date_format = "%a, %d %b %Y %H:%M:%S %Z"
                    curr_startdate = datetime.datetime.strptime(curr_startdate, date_format)
                    curr_enddate = datetime.datetime.strptime(curr_enddate, date_format)
                    rid = st.selectbox("Enter the new Room ID", room_ids, index = None)
                    dates = st.date_input("Enter the Reservation's Start and End Date", value=(curr_startdate, curr_enddate))
                    if st.button("Update", use_container_width=True):
                        if len(dates) == 2:
                            startdate = dates[0]
                            enddate = dates[1]
                            if ruid and rid and startdate and enddate:
                                requests.put(url + "/dataops/roomunavailable/" + str(ruid), json={"ruid" : ruid, "rid" : rid, "startdate" : str(startdate), "enddate" : str(enddate)}).json()
                                st.success("The record was successfully updated")
                        else:
                            st.warning("Please select a start and end date for the reservation")
            
            if selected_entity == "Room":
                st.header("")
                rooms = requests.get(url + "/dataops/room").json()
                room_ids = [str(room["rid"]) for room in rooms if room["rid"] != -1]
                rid = st.selectbox("Enter the Room ID", room_ids, index = None)
                if rid:
                    selected_room = requests.get(url + "/dataops/room/" + rid).json()
                    hotels = requests.get(url + "/dataops/hotel").json()
                    hotel_ids = [str(hotel["hid"]) for hotel in hotels if hotel["hid"] != -1]
                    roomdescriptions = requests.get(url + "/dataops/roomdescription").json()
                    roomdescription_ids = [str(roomdescription["rdid"]) for roomdescription in roomdescriptions if roomdescription["rdid"] != -1]
                    curr_hid = selected_room["hid"]
                    curr_rdid = selected_room["rdid"]
                    curr_rprice = selected_room["rprice"]
                    hid = st.selectbox("Enter the new Hotel ID", hotel_ids, index=None)
                    rdid = st.selectbox("Enter the new Room Description ID", roomdescription_ids, index=None)
                    rprice = st.text_input("Enter the new Room Price", value=curr_rprice)
                    if st.button("Update", use_container_width=True):
                        if rid and hid and rdid and rprice:
                            if is_float(rprice):
                                requests.put(url + "/dataops/room/" + str(rid), json={"rid" : rid, "hid" : hid, "rdid" : rdid, "rprice" : float(rprice)}).json()
                                st.success("The record was successfully updated")
                            else:
                                st.warning("The room's price must be a positive numerical value")
                        else:
                            st.warning("Please fill all the above fields")
            
            if selected_entity == "Hotel":
                st.header("")
                hotels = requests.get(url + "/dataops/hotel").json()
                hotel_ids = [str(hotel["hid"]) for hotel in hotels if hotel["hid"] != -1]
                hid = st.selectbox("Enter Hotel ID", hotel_ids, index=None)
                if hid:
                    selected_hotel = requests.get(url + "/dataops/hotel/" + hid).json()
                    chains = requests.get(url + "/dataops/chains").json()
                    chains_ids = [str(chain["chid"]) for chain in chains if chain["chid"] != -1]
                    curr_chid = selected_hotel["chid"]
                    curr_hcity = selected_hotel["hcity"]
                    curr_hname = selected_hotel["hname"]

                    chid = st.selectbox("Enter the new Chain ID", chains_ids, index=None)
                    hcity = st.text_input("Enter the new Hotel City", value=curr_hcity)
                    hname = st.text_input("Enter the new Hotel Name", value=curr_hname)
                    if st.button("Update", use_container_width=True):
                        if chid and hcity and hid and hname:
                            requests.put(url + "/dataops/hotel/" + str(hid), json={"chid" : chid, "hcity" : hcity, "hid" : hid, "hname" : hname}).json()
                            st.success("The record was successfully updated")
                        else:
                            st.warning("Please fill all the fields above")
                            
            if selected_entity == "Room Description":
                st.header("")
                roomdescriptions = requests.get(url + "/dataops/roomdescription").json()
                roomdescription_ids = [str(roomdescription["rdid"]) for roomdescription in roomdescriptions if roomdescription["rdid"] != -1]
                rdid = st.selectbox("Enter Room Description ID", roomdescription_ids, index=None)
                if rdid: 
                    selected_room_description = requests.get(url + "/dataops/roomdescription/" + rdid).json()
                    curr_capacity = selected_room_description["capacity"]
                    curr_ishandicap = selected_room_description["ishandicap"]
                    curr_rname = selected_room_description["rname"]
                    curr_rtype = selected_room_description["rtype"]
                    
                    room_constraints = {
                        "Standard": {"capacity": {1}, "types": {"Basic", "Premium"}, "idx" : 0},
                        "Standard Queen": {"capacity": {1, 2}, "types": {"Basic", "Premium", "Deluxe"}, "idx" : 1},
                        "Standard King": {"capacity": {2}, "types": {"Basic", "Premium", "Deluxe"}, "idx" : 2},
                        "Double Queen": {"capacity": {4}, "types": {"Basic", "Premium", "Deluxe"}, "idx" : 3},
                        "Double King": {"capacity": {4, 6}, "types": {"Basic", "Premium", "Deluxe", "Suite"}, "idx" : 4},
                        "Triple King": {"capacity": {6}, "types": {"Deluxe", "Suite"}, "idx" : 5},
                        "Executive Family": {"capacity": {4, 6, 8}, "types": {"Deluxe", "Suite"}, "idx" : 6},
                        "Presidential": {"capacity": {4, 6, 8}, "types": {"Suite"}, "idx" : 7}
                    }
                    
                    idx = room_constraints[curr_rname]["idx"]
                    rname = st.radio("Choose Room Name", list(room_constraints.keys()), index=idx)
                    constraints = room_constraints.get(rname, {"capacity": set(), "types": set()})
                    rtype = st.radio("Choose Room Type", constraints["types"], index=None)
                    capacity = st.radio("Choose Capacity Of Guests", constraints["capacity"],index=None)
                    ishandicap = st.radio("Choose Handicapped Accessibility", {False, True}, index=None)
                    
                    if st.button("Update", use_container_width=True):
                        if capacity and (ishandicap == True or ishandicap == False) and rdid and rname and rtype:
                            requests.put(url + "/dataops/roomdescription/" + str(rdid), json={"capacity" : capacity, "ishandicap" : ishandicap, "rdid" : rdid, "rname" : rname, "rtype" : rtype}).json()
                            st.success("The record was successfully updated")
                        else:
                            st.warning("Please fill all the fields above")

                    
        elif crud_choice == "Delete":
            selected_entity = st.selectbox("Select Entity to Delete", create_entities, index=None)
            if selected_entity == "Chain":
                st.header("")
                chains = requests.get(url + "/dataops/chains").json()
                chain_ids = [str(chain["chid"]) for chain in chains if chain["chid"] != -1]
                chid = st.selectbox("Enter Chain ID", chain_ids, index=None)
                if chid:
                    if st.button("Delete", use_container_width=True):
                        related_hotels = requests.get(url + "/dataops/hotel/bychid/" + str(chid)).json()
                        if related_hotels == "Not Found":
                            requests.delete(url + "/dataops/chains/" + str(chid))
                            st.success("The record was successfully deleted")
                        else:
                            st.warning("There is a hotel associated with this chain")
                            st.subheader("Table of all hotels (hid) associated with this chain")
                            st.table(related_hotels)
                            
            if selected_entity == "Login":
                st.header("")
                logins = requests.get(url + "/dataops/login").json()
                login_ids = [str(login["lid"]) for login in logins if login["lid"] != -1]
                lid = st.selectbox("Enter Login ID", login_ids, index=None)
                if lid:
                    if st.button("Delete", use_container_width=True):
                        requests.delete(url + "/dataops/login/" + str(lid))
                        st.success("The record was successfully deleted")
                        
                        
            if selected_entity == "Employee":
                st.header("")
                employees = requests.get(url + "/dataops/employee").json()
                employee_ids = [str(employee["eid"]) for employee in employees if employee["eid"] != -1]
                eid = st.selectbox("Enter Employee ID", employee_ids, index=None)
                if eid:
                    if st.button("Delete", use_container_width=True):
                        related_logins = requests.get(url + "/dataops/login/byemployeeid/" + str(eid)).json()
                        if related_logins == "Not Found":
                            requests.delete(url + "/dataops/employee/" + str(eid))
                            st.success("The record was successfully deleted")
                        else:
                            st.warning("There is a login associated with this employee")
                            st.subheader("Table of all logins (lid) associated with this employee")
                            st.table(related_logins)
            
            if selected_entity == "Reserve":
                st.header("")
                reserves = requests.get(url + "/dataops/reserve").json()
                reserve_ids = [str(reserve["reid"]) for reserve in reserves if reserve["reid"] != -1]
                reid = st.selectbox("Enter Reservation ID", reserve_ids, index=None)
                if reid:
                    if st.button("Delete", use_container_width=True):
                        requests.delete(url + "/dataops/reserve/" + str(reid))
                        st.success("The record was successfully deleted")
            
            if selected_entity == "Room Unavailable":
                st.header("")
                roomunavailables = requests.get(url + "/dataops/roomunavailable").json()
                roomunavailable_ids = [str(roomunavailable["ruid"]) for roomunavailable in roomunavailables if roomunavailable["ruid"] != -1]
                ruid = st.selectbox("Enter Room Unavailable ID", roomunavailable_ids, index = None)
                if ruid:
                    if st.button("Delete", use_container_width=True):
                        related_reserves = requests.get(url + "/dataops/reserve/byruid/" + str(ruid)).json()
                        if related_reserves == "Not Found":
                            requests.delete(url + "/dataops/roomunavailable/" + str(ruid))
                            st.success("The record was successfully deleted")
                        else:
                            st.warning("There is a reservation associated with this unavailable room")
                            st.subheader("Table of all reservations (reid) associated with this unavailable room")
                            st.table(related_reserves)
                            
            if selected_entity == "Room":
                st.header("")
                rooms = requests.get(url + "/dataops/room").json()
                room_ids = [str(room["rid"]) for room in rooms if room["rid"] != -1]
                rid = st.selectbox("Enter the Room ID", room_ids, index = None)
                if rid:
                    if st.button("Delete", use_container_width=True):
                        related_roomunavailable = requests.get(url + "/dataops/roomunavailable/byrid/" + str(rid)).json()
                        if related_roomunavailable == "Not Found":
                            requests.delete(url + "/dataops/room/" + str(rid))
                            st.success("The record was successfully deleted")
                        else:
                            st.warning("There is an unavailable room associated with this room")
                            st.subheader("Table of all unavailable rooms (ruid) associated with this room")
                            st.table(related_roomunavailable)
                            
            if selected_entity == "Hotel":
                st.header("")
                hotels = requests.get(url + "/dataops/hotel").json()
                hotel_ids = [str(hotel["hid"]) for hotel in hotels if hotel["hid"] != -1]
                hid = st.selectbox("Enter Hotel ID", hotel_ids, index=None)
                if hid:
                    if st.button("Delete", use_container_width=True):
                        related_employees = requests.get(url + "/dataops/employee/byhid/" + str(hid)).json()
                        if related_employees == "Not Found":
                            related_rooms = requests.get(url + "/dataops/room/byhid/" + str(hid)).json()
                            if related_rooms == "Not Found":
                                requests.delete(url + "/dataops/hotel/" + str(hid))
                                st.success("The record was successfully deleted")
                            else:
                                st.warning("There is a room associated with this hotel")
                                st.subheader("Table of all rooms (rid) associated with this hotel")
                                st.table(related_rooms)
                        else:
                            st.warning("There is an employee associated with this hotel")
                            st.subheader("Table of all employees (eid) associated with this hotel")
                            st.table(related_employees)
            
            if selected_entity == "Room Description":
                st.header("")
                roomdescriptions = requests.get(url + "/dataops/roomdescription").json()
                roomdescription_ids = [str(roomdescription["rdid"]) for roomdescription in roomdescriptions if roomdescription["rdid"] != -1]
                rdid = st.selectbox("Enter Room Description ID", roomdescription_ids, index=None)
                if rdid: 
                    if st.button("Delete", use_container_width=True):
                        related_rooms = requests.get(url + "/dataops/room/byrdid/" + str(rdid)).json()
                        if related_rooms == "Not Found":
                            requests.delete(url + "/dataops/roomdescription/" + str(rdid))
                            st.success("The record was successfully deleted")
                        else:
                            st.warning("There is a room associated with this description")
                            st.subheader("Table of all rooms (rid) associated with this description")
                            st.table(related_rooms)
            
            if selected_entity == "Client":
                st.header("")
                clients = requests.get(url + "/dataops/client").json()
                client_ids = [str(client["clid"]) for client in clients if client ["clid"] != -1]
                clid = st.selectbox("Enter Client ID", client_ids, index=None)
                if clid:
                    if st.button("Delete", use_container_width=True):
                        related_reserves = requests.get(url + "/dataops/reserve/byclid/" + str(clid)).json()
                        if related_reserves == "Not Found" :
                            requests.delete(url + "/dataops/client/" + str(clid))
                            st.success("The record was successfully deleted")
                        else:
                            st.warning("There is a reservation associated with this client")
                            st.subheader("Table of all reservations (reid) associated with this client")
                            st.table(related_reserves)
                            
#-------------------------------------------------------------------------------------------------#
    elif choice == "Statistics":
        if st.session_state["position"] == "Administrator":
            statistic_choice = option_menu(
                    menu_title = None,
                    options = ["Global Statistics", "Local Statistics"],
                    icons= ["globe-americas", "bar-chart"],
                    orientation= "horizontal",
                    styles={"nav-link-selected": {"background-color": "SlateGrey"},"nav-link": {"font-size": "25px", "margin":"0px", "--hover-color": "LightGray"},}
                    )
        else: 
            statistic_choice = option_menu(
                    menu_title = None,
                    options = ["Local Statistics"],
                    icons= ["bar-chart"],
                    orientation= "horizontal",
                    styles={"nav-link-selected": {"background-color": "SlateGrey"},"nav-link": {"font-size": "25px", "margin":"0px", "--hover-color": "LightGray"},}
                    )
        st.sidebar.success("Logged in as " + st.session_state["position"])
        if st.session_state['login']:
            st.sidebar.success("Logged in as {}".format(st.session_state['user']))
            st.session_state['login'] = False
        if statistic_choice == "Global Statistics":
            statistic_choice = st.selectbox("Global Statistics", global_administrator, index=None)
        if st.session_state['user']:
            if statistic_choice == "Top 3 chains with the highest total revenue.":
                st.header("")
                querydata = requests.post(url + "/dataops/most/revenue", json={"eid" : int(st.session_state["eid"])}).json()
                
                if querydata == "Employee is not an Administrator":
                    st.write("You are not an Administrator and therefore do not have access to view this statistic")
                else:
                    df = pd.DataFrame(querydata)

                    # Plotting the bar chart using matplotlib
                    # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                    fig, ax = plt.subplots(figsize=(10, 4))
                    # plt.gca().set_facecolor('#D3D3D3')
                    bars = df.plot(kind='bar', x='Chain', y='Revenue', ax=ax, legend=False, color="#151C62", figsize= (9,3.5))

                    # Rotate the x-axis labels
                    plt.xticks(rotation=0, ha='center')

                    # Set axis labels and title
                    plt.xlabel('Chains')
                    plt.ylabel('Revenue Earned')
                    plt.title('Top 3 chains with the highest total revenue')
                    
                    # Set the y-axis tick labels to use locale currency format
                    formatter = ticker.ScalarFormatter(useLocale=True)
                    ax.yaxis.set_major_formatter(formatter)

                    # Format the y-axis tick labels using locale currency format
                    for tick in ax.get_yticklabels():
                        tick.set_text(locale.currency(float(tick.get_text()), grouping=True))
                    
                    # Annotate each bar with its value
                    for bar in bars.patches:
                        height = bar.get_height()
                        ax.annotate(locale.currency(height, grouping=True),
                                    xy=(bar.get_x() + bar.get_width() / 2, height-(height*.10)),
                                    xytext=(0, -1),  # 3 points vertical offset
                                    textcoords="offset points",
                                    ha='center', va='bottom', fontweight='bold', color='white')
                                        # Set pandas option
                    pd.options.display.float_format = '{:.2f}'.format
               
                    # Show the plot
                    plt.ticklabel_format(axis="y", style="plain")
                    st.pyplot(fig, use_container_width=True)

                
            elif statistic_choice == "Total reservation percentage by payment method.":
                st.header("")
                st.header("")
                
                querydata = requests.post(url + "/dataops/paymentmethod", json={"eid" : int(st.session_state["eid"])}).json()
                df = pd.DataFrame(querydata)

                # Plotting the pie chart using matplotlib
                fig, ax = plt.subplots(figsize= (10,4))
                colors = ['#5abf6e', '#bf5a5a', '#5a5fbf', '#bfad5a', '#a35abf']
                # Create the pie chart
                wedges, texts, autotexts = ax.pie(df['Reservation Percentage'], autopct='%1.1f%%', colors=colors,)

                # Add legend
                ax.legend(wedges, df['Payment Method'], title='Payment Method', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))

                # Adjust layout
                plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                # Set title
                plt.title('Total reservation percentage by payment method')
                
                # Show the plot
                # plt.ticklabel_format(axis="y", style="plain")
                st.pyplot(fig, use_container_width=True,)
                
            elif statistic_choice == "Top 3 hotel chains with the least rooms.":
                st.header("")
                querydata = requests.post(url + "/dataops/least/rooms", json={"eid" : int(st.session_state["eid"])}).json()
                df = pd.DataFrame(querydata)

                # Plotting the bar chart using matplotlib
                # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                fig, ax = plt.subplots(figsize=(15,3))
                # plt.gca().set_facecolor('#D3D3D3')
                bars = df.plot(kind='bar', x='Chain', y='Rooms Available', ax=ax, legend=False, color="#151C62")

                # Rotate the x-axis labels
                plt.xticks(rotation=45, ha='right')

                # Set axis labels and title
                plt.xlabel('Chain')
                plt.ylabel('Number of Rooms Available')
                plt.title('Top 3 hotel chains with the least rooms')
                
                # Annotate each bar with its value
                for bar in bars.patches:
                    height = bar.get_height()
                    ax.annotate(f'{height:.0f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height-(height*.10)),
                                xytext=(0, -1),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom', fontweight='bold', color = 'white')
                
                # Show the plot
                # plt.ticklabel_format(axis="y", style="plain")
                st.pyplot(fig, use_container_width=True)
                
            elif statistic_choice == "Top 5 hotels with the most client capacity.":
                st.header("")
                querydata = requests.post(url + "/dataops/most/capacity", json={"eid" : int(st.session_state["eid"])}).json()
                df = pd.DataFrame(querydata)

                # Plotting the bar chart using matplotlib
                # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                fig, ax = plt.subplots(figsize=(12, 4))
                # plt.gca().set_facecolor('#D3D3D3')
                bars = df.plot(kind='bar', x='Hotel', y='Capacity', ax=ax, legend=False, color="#151C62")

                # Rotate the x-axis labels
                plt.xticks(rotation=45, ha='right')

                # Set axis labels and title
                plt.xlabel('Hotel')
                plt.ylabel('Client Capacity')
                plt.title('Top 5 hotels with the most client capacity')
                
                # Annotate each bar with its value
                for bar in bars.patches:
                    height = bar.get_height()
                    ax.annotate(f'{height:.0f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height-(height*.10)),
                                xytext=(0, -1),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom', fontweight='bold', color='white')
                
                # Show the plot
                # plt.ticklabel_format(axis="y", style="plain")
                st.pyplot(fig, use_container_width=True)
                
            elif statistic_choice == "Top 10% of the hotels that had the most reservations.":
                st.header("")
                querydata = requests.post(url + "/dataops/most/reservation", json={"eid" : int(st.session_state["eid"])}).json()
                df = pd.DataFrame(querydata)

                # Plotting the bar chart using matplotlib
                # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                fig, ax = plt.subplots(figsize=(11, 4))
                # plt.gca().set_facecolor('#D3D3D3')
                bars = df.plot(kind='bar', x='Hotel', y='Reservations', ax=ax, legend=False, color="#151C62")

                # Rotate the x-axis labels
                plt.xticks(rotation=45, ha='right')

                # Set axis labels and title
                plt.xlabel('Hotel')
                plt.ylabel('Reservations')
                plt.title('Top 10% of the hotels that had the most reservations')
                
                # Format y-axis tick labels with commas
                ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,}'.format(int(x))))
                
                # Annotate each bar with its value
                for bar in bars.patches:
                    height = bar.get_height()
                    ax.annotate(f'{height:,.0f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height-(height*.10)),
                                xytext=(0, -1),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom', fontweight='bold', color='white')
                
                # Show the plot
                # plt.ticklabel_format(axis="y", style="plain")
                st.pyplot(fig, use_container_width=True)
            elif statistic_choice == "Top 3 month with the most reservation by chain.":
                st.header("")
                querydata = requests.post(url + "/dataops/most/profitmonth", json={"eid" : int(st.session_state["eid"])}).json()
                df = pd.DataFrame(querydata)
                
                # Pivot the DataFrame to have chains as rows and months as columns
                pivot_df = df.pivot(index='Chain', columns='Month', values='Reservations')

                # Create a dummy DataFrame containing all 12 months
                all_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                            'July', 'August', 'September', 'October', 'November', 'December']
                
                # Define colors for each month
                color_map = {
                    'January': '#5abf6e',
                    'February': '#ff5c69',
                    'March': '#5a5fbf',
                    'April': '#bfad5a',
                    'May': '#a35abf',
                    'June': '#ff99f1',
                    'July': '#706f70',
                    'August': '#c7c7f0',
                    'September': '#69f5c6',
                    'October': '#e09753',
                    'November': '#e6e856',
                    'December': '#7bb0d1'
                }

                dummy_df = pd.DataFrame(columns=all_months, index=pivot_df.index).infer_objects(copy=False).fillna(0)

                # Concatenate the actual data with the dummy DataFrame
                concat_df = pd.concat([pivot_df, dummy_df], axis=1).infer_objects(copy=False).fillna(0)

                # Remove duplicate columns (if any)
                concat_df = concat_df.loc[:,~concat_df.columns.duplicated()]

                # Sort the columns in the concatenated DataFrame
                concat_df = concat_df.reindex(all_months, axis=1)

                # Plotting the stacked bar chart
                fig, ax = plt.subplots(figsize=(10, 5))
                concat_df.plot(kind='bar', stacked=True, ax=ax, color=[color_map[col] for col in concat_df.columns])

                # Set axis labels and title
                plt.xlabel('Chain ID')
                plt.ylabel('Reservations')
                plt.title('Top 3 month with the most reservation by chain')

                # Rotate the x-axis labels
                plt.xticks(rotation=45, ha='right')

                # Annotate each bar with its value
                for i, chain in enumerate(concat_df.index):
                    sum_of_values = int(concat_df.loc[chain].sum())
                    for month in concat_df.columns:
                        value = int(concat_df.loc[chain, month])
                        if value:
                            x_pos = i
                            y_pos = concat_df.loc[chain, :month].sum() - value / 2
                            
                            # Add a light gray background patch
                            ax.add_patch(plt.Rectangle((x_pos-0.15, y_pos - 10), 0.3, 20, color='lightgray', alpha=0.5, zorder=1))
                            
                            # Add the annotation text
                            ax.text(x_pos, y_pos, str(value), ha='center', va='center')
                            
                    # Add the annotation text for sum of values
                    ax.text(x_pos, sum_of_values, str(sum_of_values), ha='center', va='bottom', fontweight='bold')
                
                # Create the legend with all 12 months
                plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))

                # Show the plot
                st.pyplot(fig, use_container_width=True)
                
        if statistic_choice == "Local Statistics" and st.session_state['user']:
            # Get all hotel IDs except -1
            hotel_ids = requests.get(url + "/dataops/hotel").json()
            hotel_ids = [str(hotel["hid"]) for hotel in hotel_ids if hotel["hid"] != -1]
            
            statistic_choice = st.selectbox("Local Statistics", local_administrator, index=None)
            if statistic_choice == "Top 5 handicap rooms that were reserved the most.":
                selected_id = st.selectbox("Hotel IDs", hotel_ids, index=None)
                st.header("")
                if selected_id:
                    querydata = requests.post(url + "/dataops/hotel/" + selected_id + "/handicaproom", json={"eid" : int(st.session_state["eid"])}).json()
                    
                    if querydata == "The hotel's chain is not accessible to this employee":
                        st.warning("As a supervisor, you do not have access to this hotel chain's statistics")
                    elif querydata == "User is not a regular employee of this hotel":
                        st.warning("As a regular employee, you do not have access to this hotel's statistics")
                    elif not querydata:
                        st.warning("This hotel does not have any handicap rooms")
                    else:
                        df = pd.DataFrame(querydata)
                        # Plotting the bar chart using matplotlib
                        # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                        fig, ax = plt.subplots(figsize=(10, 3.5))
                        # plt.gca().set_facecolor('#D3D3D3')
                        bars = df.plot(kind='bar', x='Room ID', y='Reservations', ax=ax, legend=False, color="#151C62")

                        # Rotate the x-axis labels
                        plt.xticks(rotation=0, ha='center')

                        # Set axis labels and title
                        plt.xlabel('Handicap Room ID')
                        plt.ylabel('Reservations')
                        plt.title('Top 5 handicap rooms that were reserved the most')
                        
                        # Format y-axis tick labels with commas
                        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,}'.format(int(x))))
                        
                        # Annotate each bar with its value
                        for bar in bars.patches:
                            height = bar.get_height()
                            ax.annotate(f'{height:,.0f}',
                                        xy=(bar.get_x() + bar.get_width() / 2, height-(height*.10)),
                                        xytext=(0, -1),  # 3 points vertical offset
                                        textcoords="offset points",
                                        ha='center', va='bottom', fontweight='bold',color="white")
                        
                        # Show the plot
                        # plt.ticklabel_format(axis="y", style="plain")
                        st.pyplot(fig, use_container_width=True)
                    
            elif statistic_choice == "Top 3 rooms that were the least time unavailable.":
                
                selected_id = st.selectbox("Hotel IDs", hotel_ids, index=None)
                st.header("")
                if selected_id:
                    querydata = requests.post(url + "/dataops/hotel/" + selected_id + "/leastreserve", json={"eid" : int(st.session_state["eid"])}).json()
                    
                    if querydata == "The hotel's chain is not accessible to this employee":
                        st.warning("As a supervisor, you do not have access to this hotel chain's statistics")
                    elif querydata == "User is not a regular employee of this hotel":
                        st.warning("As a regular employee, you do not have access to this hotel's statistics")
                    elif not querydata:
                        st.warning("This hotel does not have any rooms")
                    else:
                        df = pd.DataFrame(querydata)
                        # Plotting the bar chart using matplotlib
                        # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                        fig, ax = plt.subplots(figsize=(10, 3.5))
                        # plt.gca().set_facecolor('#D3D3D3')
                        bars = df.plot(kind='bar', x='Room ID', y='Days Unavailable', ax=ax, legend=False, color="#151C62")

                        # Rotate the x-axis labels
                        plt.xticks(rotation=0, ha='center')

                        # Set axis labels and title
                        plt.xlabel('Room ID')
                        plt.ylabel('Days Unavailable')
                        plt.title('Top 3 rooms that were the least time unavailable')
                        
                        # Format y-axis tick labels with commas
                        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,}'.format(int(x))))
                        
                        # Annotate each bar with its value
                        for bar in bars.patches:
                            height = bar.get_height()
                            ax.annotate(f'{height:,.0f}',
                                        xy=(bar.get_x() + bar.get_width() / 2, height - (height*.10)),
                                        xytext=(0, -1),  # 3 points vertical offset
                                        textcoords="offset points",
                                        ha='center', va='bottom', fontweight='bold',color='white')
                        
                        # Show the plot
                        # plt.ticklabel_format(axis="y", style="plain")
                        st.pyplot(fig, use_container_width=True)
            elif statistic_choice == "Top 5 clients under 30 years old that made the most reservation with a credit card.":
                
                selected_id = st.selectbox("Hotel IDs", hotel_ids, index=None)
                st.header("")
                if selected_id:
                    querydata = requests.post(url + "/dataops/hotel/" + selected_id + "/mostcreditcard", json={"eid" : int(st.session_state["eid"])}).json()
                    
                    if querydata == "The hotel's chain is not accessible to this employee":
                        st.warning("As a supervisor, you do not have access to this hotel chain's statistics")
                    elif querydata == "User is not a regular employee of this hotel":
                        st.warning("As a regular employee, you do not have access to this hotel's statistics")
                    elif not querydata:
                        st.warning("This hotel does not have any clients")
                    else:
                        df = pd.DataFrame(querydata)
                        # Plotting the bar chart using matplotlib
                        # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                        fig, ax = plt.subplots(figsize=(6, 4))
                        # plt.gca().set_facecolor('#D3D3D3')
                        bars = df.plot(kind='bar', x='Full Name', y='Credit Card Reservations', ax=ax, legend=False, color="#151C62")

                        # Rotate the x-axis labels
                        plt.xticks(rotation=45, ha='right')

                        # Set axis labels and title
                        plt.xlabel('Client Name')
                        plt.ylabel('Credit Card Reservations')
                        plt.title('Top 5 clients under 30 years old that made the most reservation with a credit card')
                        
                        ax.set_ylim(top=5)
                        # Format y-axis tick labels with commas
                        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,}'.format(int(x))))
                        
                        # Annotate each bar with its value
                        for bar in bars.patches:
                            height = bar.get_height()
                            ax.annotate(f'{height:,.0f}',
                                        xy=(bar.get_x() + bar.get_width() / 2, height - (height*.30)),
                                        xytext=(0, -1),  # 3 points vertical offset
                                        textcoords="offset points",
                                        ha='center', va='bottom', fontweight='bold', color='white')
                        
                        # Show the plot
                        # plt.ticklabel_format(axis="y", style="plain")
                        st.pyplot(fig, use_container_width=True)
                        
            elif statistic_choice == "Top 3 highest paid regular employees.":
                
                selected_id = st.selectbox("Hotel IDs", hotel_ids, index=None)
                st.header("")
                if selected_id:
                    querydata = requests.post(url + "/dataops/hotel/" + selected_id + "/highestpaid", json={"eid" : int(st.session_state["eid"])}).json()
                    
                    if querydata == "The hotel's chain is not accessible to this employee":
                        st.warning("As a supervisor, you do not have access to this hotel chain's statistics")
                    elif querydata == "User is not a regular employee of this hotel":
                        st.warning("As a regular employee, you do not have access to this hotel's statistics")
                    elif not querydata:
                        st.warning("This hotel does not have any regular employees")
                    else:
                        df = pd.DataFrame(querydata)
                        # Plotting the bar chart using matplotlib
                        # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                        fig, ax = plt.subplots(figsize=(10, 3.5))
                        # plt.gca().set_facecolor('#D3D3D3')
                        bars = df.plot(kind='bar', x='Employee Name', y='Salary', ax=ax, legend=False, color="#151C62")

                        # Rotate the x-axis labels
                        plt.xticks(rotation=45, ha='right')

                        # Set axis labels and title
                        plt.xlabel('Employee Name')
                        plt.ylabel('Salary')
                        plt.title('Top 3 highest paid regular employees')
                        
                        # Set the y-axis tick labels to use locale currency format
                        formatter = ticker.ScalarFormatter(useLocale=True)
                        ax.yaxis.set_major_formatter(formatter)

                        # Format the y-axis tick labels using locale currency format
                        for tick in ax.get_yticklabels():
                            tick_value = float(tick.get_text().replace(',', ''))
                            # Format the tick label as currency
                            tick.set_text(locale.currency(tick_value, grouping=True))
                    
                        # Annotate each bar with its value
                        for bar in bars.patches:
                            height = bar.get_height()
                            ax.annotate(locale.currency(height, grouping=True),
                                    xy=(bar.get_x() + bar.get_width() / 2, height - (height*.10)),
                                    xytext=(0, -1),  # 3 points vertical offset
                                    textcoords="offset points",
                                    ha='center', va='bottom', fontweight='bold', color='white')
                        
                        # Show the plot
                        plt.ticklabel_format(axis="y", style="plain")
                        st.pyplot(fig, use_container_width=True)
            elif statistic_choice == "Top 5 clients that received the most discounts.":
                selected_id = st.selectbox("Hotel IDs", hotel_ids, index=None)
                st.header("")
                if selected_id:
                    querydata = requests.post(url + "/dataops/hotel/" + selected_id + "/mostdiscount", json={"eid" : int(st.session_state["eid"])}).json()
                    
                    if querydata == "The hotel's chain is not accessible to this employee":
                        st.warning("As a supervisor, you do not have access to this hotel chain's statistics")
                    elif querydata == "User is not a regular employee of this hotel":
                        st.warning("As a regular employee, you do not have access to this hotel's statistics")
                    elif not querydata:
                        st.warning("This hotel does not have any reservations")
                    else:
                        df = pd.DataFrame(querydata)
                        # Plotting the bar chart using matplotlib
                        # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                        fig, ax = plt.subplots(figsize=(10, 3.5))
                        # plt.gca().set_facecolor('#D3D3D3')
                        bars = df.plot(kind='bar', x='Client ID', y='Discounts', ax=ax, legend=False, color="#151C62")

                        # Rotate the x-axis labels
                        plt.xticks(rotation=0, ha='center')

                        # Set axis labels and title
                        plt.xlabel('Client ID')
                        plt.ylabel('Total Discounted Price')
                        plt.title('Top 5 clients that received the most discounts')
                        
                        # Set the y-axis tick labels to use locale currency format
                        formatter = ticker.ScalarFormatter(useLocale=True)
                        ax.yaxis.set_major_formatter(formatter)

                        # Format the y-axis tick labels using locale currency format
                        for tick in ax.get_yticklabels():
                            tick_value = float(tick.get_text().replace(',', ''))
                            # Format the tick label as currency
                            tick.set_text(locale.currency(tick_value, grouping=True))
                    
                        # Annotate each bar with its value
                        for bar in bars.patches:
                            height = bar.get_height()
                            ax.annotate(locale.currency(height, grouping=True),
                                    xy=(bar.get_x() + bar.get_width() / 2, height - (height*0.1)),
                                    xytext=(0, -1),  # 3 points vertical offset
                                    textcoords="offset points",
                                    ha='center', va='bottom', fontweight='bold', color='white')
                        
                        # Show the plot
                        plt.ticklabel_format(axis="y", style="plain")
                        st.pyplot(fig, use_container_width=True)
                        
            elif statistic_choice == "Total reservation percentage by room type.":
                
                selected_id = st.selectbox("Hotel IDs", hotel_ids, index=None)
                st.header("")
                if selected_id:
                    querydata = requests.post(url + "/dataops/hotel/" + selected_id + "/roomtype", json={"eid" : int(st.session_state["eid"])}).json()
                    
                    if querydata == "The hotel's chain is not accessible to this employee":
                        st.warning("As a supervisor, you do not have access to this hotel chain's statistics")
                    elif querydata == "User is not a regular employee of this hotel":
                        st.warning("As a regular employee, you do not have access to this hotel's statistics")
                    elif not querydata:
                        st.warning("This hotel does not have any reservations")
                    else:
                        df = pd.DataFrame(querydata)
                        
                        
                        # Plotting the pie chart using matplotlib
                        fig, ax = plt.subplots(figsize=(10, 3.5))
                        colors = ['#5abf6e', '#bf5a5a', '#5a5fbf', '#bfad5a']
                        # Create the pie chart
                        wedges, texts, autotexts = ax.pie(df['Total Reservations'], autopct='%1.1f%%', colors=colors)

                        # Add legend
                        ax.legend(wedges, df['Room Type'], title='Room Type', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))

                        # Adjust layout
                        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                        # Set title
                        plt.title('Total reservation percentage by room type')

                        # Show the plot
                        st.pyplot(fig, use_container_width=True)

            elif statistic_choice == "Top 3 rooms that were reserved that had the least guest-to-capacity ratio.":
                
                selected_id = st.selectbox("Hotel IDs", hotel_ids, index=None)
                st.header("")
                if selected_id:
                    querydata = requests.post(url + "/dataops/hotel/" + selected_id + "/leastguests", json={"eid" : int(st.session_state["eid"])}).json()
                    
                    if querydata == "The hotel's chain is not accessible to this employee":
                        st.warning("As a supervisor, you do not have access to this hotel chain's statistics")
                    elif querydata == "User is not a regular employee of this hotel":
                        st.warning("As a regular employee, you do not have access to this hotel's statistics")
                    elif not querydata:
                        st.warning("This hotel does not have any rooms")
                    else:
                        df = pd.DataFrame(querydata)
                        # Plotting the bar chart using matplotlib
                        # fig, ax = plt.subplots(figsize=(6, 4), facecolor='#D3D3D3')
                        fig, ax = plt.subplots(figsize=(10, 3.5))
                        # plt.gca().set_facecolor('#D3D3D3')
                        bars = df.plot(kind='bar', x='Room ID', y='Guest to Capacity Ratio', ax=ax, legend=False, color="#151C62")

                        # Rotate the x-axis labels
                        plt.xticks(rotation=0, ha='center')

                        # Set axis labels and title
                        plt.xlabel('Room ID')
                        plt.ylabel('Guest to Capacity Ratio')
                        plt.title('Top 3 rooms that were reserved that had the least guest-to-capacity ratio')
                        ax.set_ylim(top=1)
                        # Format y-axis tick labels with commas
                        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.2f}'.format(float(x))))
                        
                        # Annotate each bar with its value
                        for bar in bars.patches:
                            height = bar.get_height()
                            ax.annotate(f'{height:,.2f}',
                                        xy=(bar.get_x() + bar.get_width() / 2, height - (height*.20)),
                                        xytext=(0, -1),  # 3 points vertical offset
                                        textcoords="offset points",
                                        ha='center', va='bottom', fontweight='bold', color='white')
                        
                        # Show the plot
                        # plt.ticklabel_format(axis="y", style="plain")
                        st.pyplot(fig, use_container_width=True)
#-------------------------------------------------------------------------------------------------#

    elif choice == "Login" or choice == "Logout":
        st.image('Hotel_Analytical_System_1.png', use_column_width=True)
        st.markdown('<h2 class="fade-in">Welcome to our Hotel Analytical System!🏨</h2>', unsafe_allow_html=True)
        if st.session_state['user']:
            st.success('You are currently logged in.')
        else:
            st.warning('Please log in using the sidebar.')

        col1, col2 = st.columns([3, 1])  # Split page into two columns, ratio 3:1

    # List of hotel photo paths
        hotel_photos = ['Chain1.png', 'Chain2.png', 'Chain3.png', 'Chain4.png', 'Chain5.png']

    # Display hotel photos in the right column
        with col2:
            st.write("<h3 class='fade-in'>Our Biggest Users:</h3>", unsafe_allow_html=True)
            for photo in hotel_photos:
                st.image(photo, width=200, caption='')

        about_text = """
    <div class="fade-in">
        <strong>About:</strong>
    
    Our Hotel Analytical System is designed to streamline the process of managing hotel reservations, providing hotel staff with a user-friendly interface for handling bookings, accessing statistics, and performing administrative tasks.
      
      ***Key Features:***
          
    - **Login Page:** 🔐 
      - Easily login or create an employee account to access the system's features.

    - **Local Statistics:** 📊  
      - Access statistics related to hotel operations.

    - **Global Statistics:** 📊
      - Exclusive access for high-ranking employees to view comprehensive global statistics.

    - **Web-Based Dashboard:** 📊
      - Access valuable statistics and insights through our user-friendly web-based dashboard, enhancing your reservation management experience.

    - **Create:** ✏️ 
      - Create and manage records in the system.
      
    - **Update & Delete:** ✅❌ 
      - Users with authorization can update or delete records in the database, ensuring data accuracy and integrity.

    Experience the ease and efficiency of hotel reservation management with our intuitive solution!
    </div>
    """
        with col1:
            st.markdown(about_text, unsafe_allow_html=True)
            
            st.markdown("<h3 class='fade-in'>How to Use:</h3>", unsafe_allow_html=True)
            st.write("""
            - **Step 1:** Log in using the sidebar if you haven't already.
            - **Step 2:** Navigate to the desired feature using the sidebar menu.
            - **Step 3:** Follow the on-screen instructions to perform actions such as creating reservations, viewing statistics, and managing records.
            - **Step 4:** Enjoy the efficiency and convenience of our Hotel Reservation Management System!
            """)
        if not st.session_state['user']:
            st.sidebar.subheader("Login Section")
            username = st.sidebar.text_input("User Name")
            password = st.sidebar.text_input("Password", type='password')
            if st.session_state['logout']:
                st.sidebar.success("You have successfully logged out")
                st.session_state['logout'] = False
            if st.sidebar.button("Login"):
                if username and password:
                    data = requests.get(url + "/dataops/login/byusernamepassword",
                        params = {
                            "username" : username,
                            "password" : password
                            }
                        ).json()         

                    if data == "Not Found":
                        st.sidebar.warning("The Username or Password is incorrect")
                    else:
                        st.session_state['user'] = data["username"]
                        st.session_state['password'] = data["password"]
                        st.session_state['eid'] = data["eid"]
                        st.session_state['login'] = True
                        st.session_state['position'] = data["position"]
                        st.rerun()
                else:
                    st.sidebar.warning("Please input a Username and Password")
        else:
            st.sidebar.subheader("Logout Section")
            if not st.session_state['login']:
                st.sidebar.warning("You are already logged in as {}".format(st.session_state["user"]))
            if st.sidebar.button("Logout"):
                st.session_state['user'] = None
                st.session_state['password'] = None
                st.session_state['eid'] = None
                st.session_state['logout'] = True
                st.session_state['position'] = None
                st.rerun()
    
    elif choice == "Create Employee Account":
        st.image('Hotel_Analytical_System_1.png', use_column_width=True)
        st.markdown('<h2 class="fade-in">Welcome to our Hotel Analytical System!🏨</h2>', unsafe_allow_html=True)
        if st.session_state['user']:
            st.success('You are currently logged in.')
        else:
            st.warning('Please log in using the sidebar.')

        col1, col2 = st.columns([3, 1])  # Split page into two columns, ratio 3:1

    # List of hotel photo paths
        hotel_photos = ['Chain1.png', 'Chain2.png', 'Chain3.png', 'Chain4.png', 'Chain5.png']

    # Display hotel photos in the right column
        with col2:
            st.write("<h3 class='fade-in'>Our Biggest Users:</h3>", unsafe_allow_html=True)
            for photo in hotel_photos:
                st.image(photo, width=200, caption='')

        about_text = """
    <div class="fade-in">
        <strong>About:</strong>
    
    Our Hotel Analytical System is designed to streamline the process of managing hotel reservations, providing hotel staff with a user-friendly interface for handling bookings, accessing statistics, and performing administrative tasks.
      
      ***Key Features:***
          
    - **Login Page:** 🔐 
      - Easily login or create an employee account to access the system's features.

    - **Local Statistics:** 📊  
      - Access statistics related to hotel operations.

    - **Global Statistics:** 📊
      - Exclusive access for high-ranking employees to view comprehensive global statistics.

    - **Web-Based Dashboard:** 📊
      - Access valuable statistics and insights through our user-friendly web-based dashboard, enhancing your reservation management experience.

    - **Create:** ✏️ 
      - Create and manage records in the system.
      
    - **Update & Delete:** ✅❌ 
      - Users with authorization can update or delete records in the database, ensuring data accuracy and integrity.

    Experience the ease and efficiency of hotel reservation management with our intuitive solution!
    </div>
    """
        with col1:
            st.markdown(about_text, unsafe_allow_html=True)
            
            st.markdown("<h3 class='fade-in'>How to Use:</h3>", unsafe_allow_html=True)
            st.write("""
            - **Step 1:** Log in using the sidebar if you haven't already.
            - **Step 2:** Navigate to the desired feature using the sidebar menu.
            - **Step 3:** Follow the on-screen instructions to perform actions such as creating reservations, viewing statistics, and managing records.
            - **Step 4:** Enjoy the efficiency and convenience of our Hotel Reservation Management System!
            """)
        employee_ids = requests.get(url + "/dataops/employee").json()
        employee_ids = [employee["eid"] for employee in employee_ids if employee["eid"] != -1]
        st.sidebar.subheader("Create Account Section")
        eid = st.sidebar.selectbox("Employee ID", employee_ids, index=None)
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Create Account"):
            if username and password and eid:
                account = requests.get(url + "/dataops/login/byemployeeid/" + str(eid)).json()
                data = requests.get(url + "/dataops/login/byusername",
                    params = {
                        "username" : username
                        }
                    ).json()
                if account != "Not Found":
                    st.sidebar.warning("There is already an account for this Employee ID")
                elif data != "Not Found":
                    st.sidebar.warning("This username is already taken")
                else:
                    requests.post(url + "/dataops/login", json={"eid" : int(eid), "username" : username, "password" : password}).json()
                    st.sidebar.success("Account was created successfully")
                    
            else:
                st.sidebar.warning("Please fill all the fields above")
                    
if __name__ == "__main__":
    main()

#input_df = user_input_features()

