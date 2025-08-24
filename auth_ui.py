import streamlit as st
import database as db


def show_login_form():
    """Show login form in sidebar"""
    with st.sidebar:
        st.header("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                if username and password:
                    conn = db.create_connection()
                    user = db.authenticate_user(conn, username, password)
                    if user:
                        st.session_state["user_id"] = user[0]
                        st.session_state["username"] = user[1]
                        st.session_state["logged_in"] = True
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter username and password")

        with col2:
            if st.button("Register"):
                if username and password:
                    conn = db.create_connection()
                    user_id = db.create_user(conn, username, password)
                    if user_id:
                        st.success(f"Account created for {username}!")
                        st.info("You can now login with your credentials")
                    else:
                        st.error("Username already exists or error occurred")
                else:
                    st.warning("Please enter username and password")


def show_user_info():
    """Show user information and logout button"""
    with st.sidebar:
        st.header(f"👤 {st.session_state.get('username', 'User')}")

        if st.button("Logout"):
            # Clear session state
            for key in ["user_id", "username", "logged_in"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("Logged out successfully!")
            st.rerun()

        # Show user's submissions
        if "user_id" in st.session_state:
            conn = db.create_connection()
            user_submissions = db.get_user_submissions(
                conn, st.session_state["user_id"]
            )

            if not user_submissions.empty:
                st.subheader("Your Submissions")
                for _, row in user_submissions.iterrows():
                    with st.expander(
                        f"'{row['dialect_word']}' from {row['location_text']}"
                    ):
                        st.write(
                            f"**Privacy:** {'Public' if row['is_public'] else 'Private'}"
                        )
                        st.write(
                            f"**Verified:** {'Yes' if row['is_verified'] else 'No'}"
                        )

                        # Privacy toggle
                        if st.button(
                            f"Make {'Private' if row['is_public'] else 'Public'}",
                            key=f"toggle_{row['id']}",
                        ):
                            db.toggle_submission_privacy(
                                conn, row["id"], st.session_state["user_id"]
                            )
                            st.rerun()

                        # Delete button
                        if st.button("Delete", key=f"delete_{row['id']}"):
                            if db.delete_submission(
                                conn, row["id"], st.session_state["user_id"]
                            ):
                                st.success("Submission deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete submission")


def check_auth():
    """Check if user is authenticated"""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    return st.session_state["logged_in"]


def get_current_user():
    """Get current user information"""
    if check_auth():
        return {
            "id": st.session_state.get("user_id"),
            "username": st.session_state.get("username"),
        }
    return None
