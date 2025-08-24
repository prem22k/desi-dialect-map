# Data Privacy & Security Guide

## 🔒 **Current Data Accessibility Status**

### **⚠️ IMPORTANT: Your app currently has NO privacy controls by default!**

**What this means:**

- **All submissions are publicly visible** to anyone who visits your app
- **All images are publicly accessible**
- **No user authentication** - anyone can submit content
- **No data ownership** - users can't claim or control their submissions
- **No content moderation** - no way to remove inappropriate content

## 🛡️ **Privacy Features I've Added (Optional)**

I've created an **optional authentication system** that you can integrate to add privacy controls:

### **✅ What the Auth System Provides:**

1. **User Accounts**

   - Users can create accounts with username/password
   - Passwords are securely hashed (SHA-256)
   - No email required (optional)

2. **Privacy Controls**

   - Users can make submissions **public** or **private**
   - Private submissions are only visible to the owner
   - Public submissions are visible to everyone

3. **Data Ownership**

   - Users can only modify/delete their own submissions
   - Users can see all their submissions in one place
   - Users can toggle privacy settings anytime

4. **Content Moderation**
   - Users can delete their own submissions
   - Users can change privacy settings
   - Better control over what's publicly visible

## 🚀 **How to Enable Privacy Controls**

### **Option 1: Quick Integration (Recommended)**

1. **Import the auth module** in your `app.py`:

```python
import auth_ui as auth
```

2. **Add authentication to your sidebar**:

```python
# In your sidebar
if not auth.check_auth():
    auth.show_login_form()
else:
    auth.show_user_info()
```

3. **Update submission calls** to include user ID:

```python
# Before (no privacy)
submission_id = db.add_submission(conn, dialect_word, location_text, image_data)

# After (with privacy)
user = auth.get_current_user()
submission_id = db.add_submission(
    conn, dialect_word, location_text, image_data,
    user_id=user['id'] if user else None,
    is_public=True  # or False for private
)
```

### **Option 2: Keep Current Setup (No Privacy)**

If you want to keep the current open setup:

- **No changes needed** - everything stays public
- **Good for:** Public datasets, research, community projects
- **Consider:** Adding a disclaimer about public data

## 🔍 **What Users Can See/Do**

### **Without Login (Public Access):**

- ✅ View all public submissions on the map
- ✅ Browse the community gallery
- ✅ Search and filter submissions
- ✅ Download public data as CSV
- ❌ Cannot submit content
- ❌ Cannot see private submissions
- ❌ Cannot modify any data

### **With Login (Authenticated Users):**

- ✅ All public access features
- ✅ Submit new content (public or private)
- ✅ View their own private submissions
- ✅ Toggle privacy of their submissions
- ✅ Delete their own submissions
- ✅ See all their submissions in one place
- ❌ Cannot see other users' private submissions
- ❌ Cannot modify others' submissions

## 📊 **Privacy Levels Explained**

### **Public Submissions:**

- **Visible to:** Everyone (logged in or not)
- **Appears on:** Public map, gallery, search results
- **Included in:** CSV exports, statistics
- **Good for:** Sharing knowledge, community building

### **Private Submissions:**

- **Visible to:** Only the submitting user
- **Appears on:** User's personal dashboard only
- **Included in:** User's personal data only
- **Good for:** Personal notes, work in progress

## 🚨 **Security Considerations**

### **Current Limitations:**

1. **No email verification** - usernames can be anything
2. **No password complexity requirements**
3. **No rate limiting** - users could spam submissions
4. **No admin panel** - no way to moderate all content
5. **No data backup** - if Streamlit Cloud resets, data is lost

### **For Production Use, Consider:**

1. **Email verification** for user accounts
2. **Password complexity requirements**
3. **Rate limiting** for submissions
4. **Admin panel** for content moderation
5. **Data backup** to external storage
6. **User terms of service** and privacy policy

## 🎯 **Recommendations**

### **For MVP/Testing:**

- **Keep current setup** - simple and works immediately
- **Add privacy disclaimer** about public data
- **Monitor submissions** for inappropriate content

### **For Community Use:**

- **Enable authentication** for better control
- **Set default privacy** to public (encourage sharing)
- **Add content guidelines** and community rules

### **For Production/Research:**

- **Full authentication system** with email verification
- **Admin moderation tools**
- **Data export controls**
- **User consent and privacy policy**

## 🔧 **Quick Privacy Test**

To test if privacy is working:

1. **Create two user accounts**
2. **Submit content with different privacy settings**
3. **Log in/out to verify access control**
4. **Check that private submissions are hidden**

## 📝 **Privacy Policy Template**

If you enable authentication, consider adding this to your app:

```
Privacy Policy:
- Public submissions are visible to everyone
- Private submissions are only visible to you
- You can change privacy settings anytime
- You can delete your submissions anytime
- We do not share your personal information
- Data is stored locally on Streamlit Cloud servers
```

---

**💡 Bottom Line:** Your current setup is perfect for an open, community-driven project. The privacy features I've added are optional and can be integrated when you're ready for more control over data access.
