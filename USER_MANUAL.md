# 📘 JalRakshak – User Operational Manual

Welcome to **JalRakshak**! This user manual explains the operational mechanics of the platform for both citizens reporting issues and municipal authority operators resolving municipal leakages.

---

## 👥 1. Citizen Portal Guide

### 🔑 A. Account Registration & Login
1. Navigate to the landing page and click **Sign Up** in the upper right.
2. Complete your Full Name, Email, and Password. Make sure the role selector is set to **Citizen Reporter**.
3. Upon success, you will be redirected to the **Login** gateway. Use your registered credentials to sign in. 
   *(Alternatively, click the **Citizen Account** demo badge on the Login screen to access the sandbox instantly!)*

### 💧 B. Reporting a Water Leakage
1. Once logged in, click the glowing **Report Leak** button on your Citizen Dashboard.
2. **Snapping Coordinates**: The browser will request GPS location access. Granting permission snaps your exact coordinates automatically. If GPS is unavailable, the portal defaults to a localized section of Hyderabad.
3. **Fill in Details**:
   * **Issue Title**: Give a concise summary (e.g., "Municipal pipe burst near lane 3").
   * **Optional Description**: Provide additional landmarks or details (e.g., "gushing water forming massive pooling next to the temple").
4. **Photo Upload**: Drag and drop or click the dotted box to select a photo. You will see an instant visual preview of the selected image.
5. **Submit**: Click **Submit Leak Report**. JalRakshak’s built-in **AI Engine** runs instantly behind the scenes, estimating leak severity and scanning for proximity duplicate tickets.

### 🗺️ C. Navigating Maps and Confirming Reports
1. **Interactive Map**: Look at the dark-themed leaflet map canvas. You will see colored status indicators of reported leaks.
2. **Sidebar cards sync**: Click on any card in the sidebar. The Leaflet map will glide smoothly ("fly-to") to center that specific marker.
3. **Peer Citizen Verification**:
   * Tap on any card reported by another user.
   * Click **Confirm Active Leak** on the card or map popup.
   * This increases the report's credibility score instantly, signaling to authorities that it is a verified public concern.

---

## 🏢 2. Authority Admin Portal Guide

This portal is tailored for water supply engineers and municipal dispatch officers (e.g., HMWS&SB).

### 📈 A. Analytical Dashboard Insights
1. **Aggregates Summary**: Quick statistics cards display overall active investigations, resolved issues, and citizen-led credibility confirmations.
2. **Telangana Area Spread Charts**: Review custom area distribution bars to detect which Hyderabad neighborhood (e.g. Gachibowli, Jubilee Hills, Secunderabad) is facing the highest concentration of leakage issues.
3. **Operational splits**: Track percentages of tickets currently undergoing review, active repairs, or successfully closed.

### 📋 B. Issue Management Grid and Drawer Inspector
1. **Filter Tools**: Search tickets by title or reporter name. Filter items by urgency status or severity rating.
2. **Selecting a ticket**: Click on any issue in the table. This populates the **Split-View details drawer** on the right.
3. **Audit Evidence**: Review the uploaded photo, exact GPS coordinates, user description details, and peer-verification indicators.
4. **AI Diagnostics Box**: The diagnostic panel shows the AI Visual Scan verification score (e.g. 94% leak detected) and priority prediction.

### 🔧 C. Updating Status & remarks log
1. In the status remarks panel, select the updated status dropdown:
   * **Reported**: Initial ticket log.
   * **Under Review**: assigned area engineers inspecting the site.
   * **In Progress**: repair crew, welding gear, and bypass lines dispatched.
   * **Resolved**: Seepage successfully arrested and double-checked.
2. **Log remarks**: Write comments detailing maintenance updates (e.g. "dispatched excavator to repair valve flange").
3. Click **Apply Status Change**. This refreshes analytics, updates the status badge instantly, and registers a permanent timeline item in the **Maintenance Status History** audit log.
