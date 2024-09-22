import pandas as pd
import pyrebase
import streamlit as st
from sklearn.preprocessing import LabelEncoder
import pickle

# Firebase configuration
firebaseConfig = {
    'apiKey': "AIzaSyBcRIWE_RpNBEm8_NFEy5Wlp28z72dQ5bU",
    'authDomain': "testapp-6b027.firebaseapp.com",
    'databaseURL': "https://testapp-6b027-default-rtdb.asia-southeast1.firebasedatabase.app",
    'projectId': "testapp-6b027",
    'storageBucket': "testapp-6b027.appspot.com",
    'messagingSenderId': "15502357384",
    'appId': "1:15502357384:web:656731463f4d2b2277803d",
    'measurementId': "G-3T1ZDR76YP"
}

# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Streamlit UI
st.sidebar.title("Car Price Prediction App")


# Authentication options
choice = st.sidebar.selectbox("Login/Sign Up", ["Sign Up", "Login"])

email = st.sidebar.text_input("Please enter your email address")
password = st.sidebar.text_input("Please enter your password", type="password")

if choice == "Sign Up":
    handle = st.sidebar.text_input("Please input your app handle name", value="Default")
    submit = st.sidebar.button("Create my account")

    if submit:
        try:
            # Try to create the user
            user = auth.create_user_with_email_and_password(email, password)
            st.success("Your Account is Created Successfully!")
            st.balloons()

            # Sign the user in after creating the account
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state['user'] = user

            # Store user data in the database
            db = firebase.database()
            db.child(user['localId']).child("Handle").set(handle)
            db.child(user['localId']).child("ID").set(user['localId'])

            st.title(f"WELCOME {handle}")
            st.info("You can now log in using the Login option.")

        except Exception as e:
            error_message = e.args[1]
            if "EMAIL_EXISTS" in error_message:
                st.error("This email already exists. Please log in.")
            else:
                st.error(f"An error occurred: {error_message}")

elif choice == "Login":
    login = st.sidebar.button("Login")
    
    if login:
        try:
            # Try to log the user in
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state['user'] = user
            st.success(f"Logged in as {email}")
            st.experimental_rerun()  # Rerun the app to access the main page after login

        except Exception as e:
            error_message = e.args[1]
            st.error(f"Login failed: {error_message}")

# After login, show the main page content
if 'user' in st.session_state:
    def main():
        html_temp = """
        <div style ="background-color:blue;padding:16px">
        <h2 style="color:white;text-align:center;"> Car Price Prediction Using ML </h2>
        </div>
        """
        
        st.markdown(html_temp, unsafe_allow_html=True)
        
        # Load the dataset from Google Drive
        try:
            df = pd.read_csv("https://drive.google.com/uc?export=download&id=17KxRuOK4uONRZyfYNgjoX62y2yO5KpLY")
        except Exception as e:
            st.error(f"Error loading dataset: {e}")
            return
        
        # Load the model
        try:
          
          file_path = (r"D:\capstone folder\lr_model.pkl")
          with open(file_path, 'rb') as file:
                loaded_model = pickle.load(file)
        except FileNotFoundError:
            st.error("Model file 'lr_model.pkl' not found. Make sure the file is in the correct directory.")
            return
        except Exception as e:
            st.error(f"Error loading model: {e}")
            return
        
        lb = LabelEncoder()

        st.write(' ')
        st.write(' ')
        st.markdown("""
        ##### Are you planning to sell your car? Predict the best selling price of your car.
        ##### The price of a new car reduces by 30% when sold immediately.
        ##### Avoid market frauds and predict the price with this tool!
        """)

        r1 = st.selectbox("Brand name of your car", df['name'].unique())
        r2 = st.number_input("The distance traveled by your car in Kilometers", 100, 500000, step=100)
        r3 = st.selectbox("What is the fuel type of your car?", df['fuel'].unique())
        r4 = st.selectbox("Are you an Individual, Dealer, or Trustmark Dealer?", df['seller_type'].unique())
        r5 = st.selectbox("What is the transmission type of your car?", df['transmission'].unique())
        r6 = st.selectbox("Number of previous owners?", df['owner'].unique())
        r7 = st.slider("Year of purchase", 1990, 2023)

        data_new = pd.DataFrame({
            'name': r1,
            'km_driven': r2,
            'fuel': r3,
            'seller_type': r4,
            'transmission': r5,
            'owner': r6,
            'age': r7
        }, index=[0])

        data_new['name'] = lb.fit_transform(data_new['name'])
        data_new['fuel'] = lb.fit_transform(data_new['fuel'])
        data_new['seller_type'] = lb.fit_transform(data_new['seller_type'])
        data_new['transmission'] = lb.fit_transform(data_new['transmission'])
        data_new['owner'] = lb.fit_transform(data_new['owner'])         

        if st.button('Predict'):
            try:
                pred = loaded_model.predict(data_new)
                if pred > 0:
                    st.balloons()
                message = "You can sell your car for {:.2f} lakhs".format(pred[0])
                st.success(message)
            except Exception as e:
                st.error(f"Prediction failed: {e}")
        else:
            st.warning("You can't sell this car")

    main()
    
    if st.button("Logout"):
        st.session_state.clear()  # Clear the session state
        st.success("You have been logged out.")
        st.session_state['page'] = 'signup'

if 'page' not in st.session_state:
    st.session_state['page'] = 'signup'  # Start with signup page


if st.session_state['page'] == 'login':
    login()  # Show the login page after signup
elif st.session_state['page'] == 'main' and 'user' in st.session_state:
    main()  # Show the main page only after login
else:
    st.warning("You must log in to view this page.")