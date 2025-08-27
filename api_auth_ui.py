import streamlit as st
from api_auth import api_auth, init_session_state, save_auth_to_session, load_auth_from_session, clear_auth_session
import re

def validate_phone_number(phone: str) -> bool:
    """Validate Indian phone number format"""
    # Indian phone number pattern: +91XXXXXXXXXX or 91XXXXXXXXXX or XXXXXXXXXX
    pattern = r'^(\+91|91)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def show_api_auth_sidebar():
    """Show authentication interface in sidebar"""
    init_session_state()
    load_auth_from_session()
    
    with st.sidebar:
        st.header("🔐 API Authentication")
        
        if api_auth.is_authenticated():
            show_authenticated_user()
        else:
            show_auth_options()

def show_auth_options():
    """Show authentication options for non-authenticated users"""
    auth_tab1, auth_tab2 = st.tabs(["📱 Login", "📝 Signup"])
    
    with auth_tab1:
        show_login_interface()
    
    with auth_tab2:
        show_signup_interface()

def show_login_interface():
    """Show login interface"""
    st.subheader("Login to API")
    
    # Login method selection
    login_method = st.radio("Login Method", ["Password", "OTP"], key="login_method")
    
    if login_method == "Password":
        show_password_login()
    else:
        show_otp_login()

def show_password_login():
    """Show password-based login"""
    phone = st.text_input("Phone Number", placeholder="+919876543210", key="login_phone")
    password = st.text_input("Password", type="password", key="login_password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login", use_container_width=True):
            if phone and password:
                if not validate_phone_number(phone):
                    st.error("Please enter a valid Indian phone number")
                    return
                
                result = api_auth.login_with_password(phone, password)
                if "access_token" in result:
                    save_auth_to_session()
                    st.success("Login successful!")
                    st.rerun()
                elif "error" in result:
                    st.error(f"Login failed: {result['error']}")
                else:
                    st.error("Login failed. Please check your credentials.")
            else:
                st.warning("Please enter phone number and password")
    
    with col2:
        if st.button("Forgot Password?", use_container_width=True):
            st.session_state.show_forgot_password = True

def show_otp_login():
    """Show OTP-based login"""
    phone = st.text_input("Phone Number", placeholder="+919876543210", key="otp_login_phone")
    
    if not st.session_state.api_auth_otp_sent:
        if st.button("Send OTP", use_container_width=True):
            if phone:
                if not validate_phone_number(phone):
                    st.error("Please enter a valid Indian phone number")
                    return
                
                result = api_auth.send_login_otp(phone)
                if "status" in result and result["status"] in ["success", "signup_required"]:
                    st.session_state.api_auth_phone = phone
                    st.session_state.api_auth_otp_sent = True
                    if result["status"] == "signup_required":
                        st.warning("Phone number not registered. Please signup first.")
                    else:
                        st.success("OTP sent successfully!")
                    st.rerun()
                else:
                    st.error("Failed to send OTP. Please try again.")
            else:
                st.warning("Please enter phone number")
    else:
        otp = st.text_input("Enter OTP", placeholder="123456", key="otp_login_code")
        consent = st.checkbox("I consent to data collection", value=True, key="login_consent")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Verify OTP", use_container_width=True):
                if otp and consent:
                    result = api_auth.verify_login_otp(
                        st.session_state.api_auth_phone, 
                        otp, 
                        consent
                    )
                    if "access_token" in result:
                        save_auth_to_session()
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid OTP. Please try again.")
                else:
                    st.warning("Please enter OTP and give consent")
        
        with col2:
            if st.button("Resend OTP", use_container_width=True):
                result = api_auth.resend_login_otp(st.session_state.api_auth_phone)
                if "status" in result and result["status"] == "success":
                    st.success("OTP resent successfully!")
                else:
                    st.error("Failed to resend OTP")
        
        if st.button("Back to Login", use_container_width=True):
            st.session_state.api_auth_otp_sent = False
            st.rerun()

def show_signup_interface():
    """Show signup interface"""
    st.subheader("Create New Account")
    
    phone = st.text_input("Phone Number", placeholder="+919876543210", key="signup_phone")
    name = st.text_input("Full Name", placeholder="Your Name", key="signup_name")
    email = st.text_input("Email", placeholder="your.email@example.com", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    consent = st.checkbox("I consent to data collection", value=True, key="signup_consent")
    
    if st.button("Send Signup OTP", use_container_width=True):
        if phone and name and email and password and confirm_password and consent:
            # Validation
            if not validate_phone_number(phone):
                st.error("Please enter a valid Indian phone number")
                return
            if not validate_email(email):
                st.error("Please enter a valid email address")
                return
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            if len(password) < 8:
                st.error("Password must be at least 8 characters long")
                return
            
            # Store signup data
            st.session_state.api_auth_signup_data = {
                "phone": phone,
                "name": name,
                "email": email,
                "password": password,
                "consent": consent
            }
            
            result = api_auth.send_signup_otp(phone)
            if "status" in result and result["status"] == "success":
                st.session_state.api_auth_phone = phone
                st.session_state.api_auth_otp_sent = True
                st.success("OTP sent successfully!")
                st.rerun()
            else:
                st.error("Failed to send OTP. Please try again.")
        else:
            st.warning("Please fill all fields and give consent")
    
    # Show OTP verification if OTP was sent
    if st.session_state.api_auth_otp_sent and st.session_state.api_auth_phone == phone:
        st.markdown("---")
        st.subheader("Verify OTP")
        
        otp = st.text_input("Enter OTP", placeholder="123456", key="signup_otp_code")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Verify & Create Account", use_container_width=True):
                if otp and st.session_state.api_auth_signup_data:
                    data = st.session_state.api_auth_signup_data
                    result = api_auth.verify_signup_otp(
                        data["phone"],
                        otp,
                        data["name"],
                        data["email"],
                        data["password"],
                        data["consent"]
                    )
                    if "access_token" in result:
                        save_auth_to_session()
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create account. Please try again.")
                else:
                    st.warning("Please enter OTP")
        
        with col2:
            if st.button("Resend OTP", use_container_width=True):
                result = api_auth.resend_signup_otp(st.session_state.api_auth_phone)
                if "status" in result and result["status"] == "success":
                    st.success("OTP resent successfully!")
                else:
                    st.error("Failed to resend OTP")

def show_authenticated_user():
    """Show interface for authenticated users"""
    user_info = api_auth.get_user_info()
    
    if user_info:
        st.success(f"✅ Logged in as {user_info.get('phone_number', 'User')}")
        
        # Get detailed user info
        detailed_info = api_auth.get_current_user()
        if "error" not in detailed_info:
            st.info(f"👤 {detailed_info.get('name', 'User')}")
            st.info(f"📧 {detailed_info.get('email', 'No email')}")
            st.info(f"📍 {detailed_info.get('place', 'No location')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Change Password", use_container_width=True):
            st.session_state.show_change_password = True
    
    with col2:
        if st.button("Logout", use_container_width=True):
            clear_auth_session()
            st.success("Logged out successfully!")
            st.rerun()
    
    # Change password interface
    if st.session_state.get("show_change_password", False):
        st.markdown("---")
        st.subheader("Change Password")
        
        current_password = st.text_input("Current Password", type="password", key="change_current_password")
        new_password = st.text_input("New Password", type="password", key="change_new_password")
        confirm_new_password = st.text_input("Confirm New Password", type="password", key="change_confirm_password")
        
        if st.button("Update Password", use_container_width=True):
            if current_password and new_password and confirm_new_password:
                if new_password != confirm_new_password:
                    st.error("New passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long")
                else:
                    result = api_auth.change_password(current_password, new_password)
                    if "message" in result:
                        st.success("Password changed successfully!")
                        st.session_state.show_change_password = False
                        st.rerun()
                    else:
                        st.error("Failed to change password")
            else:
                st.warning("Please fill all password fields")
        
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_change_password = False
            st.rerun()

def show_forgot_password():
    """Show forgot password interface"""
    if st.session_state.get("show_forgot_password", False):
        st.markdown("---")
        st.subheader("Forgot Password")
        
        phone = st.text_input("Phone Number", placeholder="+919876543210", key="forgot_phone")
        
        if not st.session_state.get("forgot_otp_sent", False):
            if st.button("Send Reset OTP", use_container_width=True):
                if phone:
                    if not validate_phone_number(phone):
                        st.error("Please enter a valid Indian phone number")
                        return
                    
                    result = api_auth.forgot_password_init(phone)
                    if "status" in result and result["status"] == "success":
                        st.session_state.forgot_phone = phone
                        st.session_state.forgot_otp_sent = True
                        st.success("Reset OTP sent successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to send reset OTP")
                else:
                    st.warning("Please enter phone number")
        else:
            otp = st.text_input("Enter OTP", placeholder="123456", key="forgot_otp")
            new_password = st.text_input("New Password", type="password", key="forgot_new_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="forgot_confirm_password")
            
            if st.button("Reset Password", use_container_width=True):
                if otp and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters long")
                    else:
                        result = api_auth.forgot_password_confirm(
                            st.session_state.forgot_phone,
                            otp,
                            new_password,
                            confirm_password
                        )
                        if "status" in result and result["status"] == "success":
                            st.success("Password reset successfully!")
                            st.session_state.show_forgot_password = False
                            st.session_state.forgot_otp_sent = False
                            st.rerun()
                        else:
                            st.error("Failed to reset password")
                else:
                    st.warning("Please fill all fields")
            
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_forgot_password = False
                st.session_state.forgot_otp_sent = False
                st.rerun()

def main_api_interface():
    """Main API interface for authenticated users"""
    if not api_auth.is_authenticated():
        st.warning("Please login to access API features")
        return
    
    st.success("🔗 Connected to Indic Corpus Collections API")
    
    # Show user info
    user_info = api_auth.get_current_user()
    if "error" not in user_info:
        st.info(f"Welcome, {user_info.get('name', 'User')}!")
    
    # API features will be added here in next phases
    st.info("🚧 API features coming soon...")
    st.info("• Submit dialect records to centralized database")
    st.info("• Browse records from across India")
    st.info("• View analytics and user contributions")
    st.info("• Search nearby records and filter by categories")
