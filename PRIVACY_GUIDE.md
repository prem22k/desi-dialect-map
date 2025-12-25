# Data Privacy & Security Guide

## 🔒 **Authentication & Data Security**

The **Desi Dialect Map** integrates with the **Indic Corpus Collections API** to ensure secure data handling and user authentication.

### **Authentication**

-   **User Accounts:** Users must log in to contribute data. Authentication is handled via the Indic Corpus Collections API using OTP (One-Time Password) verification.
-   **Secure Tokens:** The application uses secure Bearer tokens to authenticate API requests. These tokens are stored in the session state and are not persisted to disk.

### **Data Handling**

-   **Data Storage:** All submitted data (images, text, location) is stored securely in the Indic Corpus Collections API database. The application does not store user data locally.
-   **Public Visibility:**
    -   **Map & Gallery:** Submissions are visualized on the public map and gallery to foster community learning.
    -   **Attribution:** Submissions are linked to the user's profile (if applicable) or anonymized based on API settings.

### **Privacy Controls**

-   **User Consent:** Users provide consent when submitting data, acknowledging that it will be part of the public corpus.
-   **Data Ownership:** Users retain rights to their contributions as per the terms of the Indic Corpus Collections API.

## 🛡️ **Best Practices**

-   **Do not upload sensitive personal information.**
-   **Ensure you have the right to share the images you upload.**
-   **Respect the privacy of others when taking photos of public scenes.**

For more details on the API's privacy policy, please refer to the Indic Corpus Collections documentation.


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
