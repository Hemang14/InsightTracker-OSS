# 📊 **InsightTracker OSS**

OSS Dashboard is a web application designed to track and visualize open-source project metrics, including commits, pull requests, and issue resolution trends. The dashboard provides an **interactive UI** for project monitoring, label insights, and historical analysis.

## 🚀 Features

### **1️⃣ Dashboard Overview**
- Displays a high-level overview of all tracked **Open-Source Software (OSS)** projects.
- Includes **search functionality** and **filter options**.

### **2️⃣ Project Details Page**
- Click on any project to see **detailed metrics**.
- Displays **soft labels** assigned based on activity trends.
- Provides **historical data insights** and **predictive analysis**.

### **3️⃣ Monthly Selector**
- Allows users to **select a specific month** to view **historical soft labels**.
- Displays **label insights** for each month.

### **4️⃣ Time-Series Graphs**
- Interactive graphs for:
  - **Commits**
  - **Pull Requests**
  - **Issues**
- Users can toggle between **weekly, monthly, and yearly views**.

### **5️⃣ Label Insights**
- Each project is assigned a **soft label** based on activity metrics.
- Label categories:
  - ✅ **Accelerating** - Rapid growth.
  - 🔵 **Consolidating** - Moderate growth.
  - ⚪ **Maintaining** - Stable operation.
  - 🟡 **Plateauing** - Little to no growth.
  - 🟠 **Declining** - Noticeable decline.
  - 🔴 **Crisis** - Project at risk.
  - 🟢 **Reviving** - Signs of recovery.

## 🛠️ Tech Stack
- **Frontend**: React.js, Material-UI
- **Charts**: Recharts
- **Routing**: React Router
- **Backend (Future Implementation)**: Node.js, Express
- **Database (Future Implementation)**: MongoDB or PostgreSQL

## ⚡ Installation Guide

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/yourusername/oss-dashboard.git
cd oss-dashboard
npm install
npm install react-router-dom @mui/material @mui/icons-material @mui/lab @mui/x-date-pickers @emotion/react @emotion/styled recharts @date-io/date-fns
npm start
```

---

# 📌 NOTES

### **🎨 UI Components**
- **Dashboard**: Displays all projects with color-coded status labels.
- **Click a project** to see **detailed insights**.
- **Project Details**: Shows real-time project statistics.
- **Displays interactive time-series graphs**.

### **📊 Example Project Data**
- The app currently uses **mock data**.
- Future versions will fetch **real data from GitHub APIs**.

### **🎯 Future Enhancements**
- ✅ **Backend API Integration** (GitHub API for real-time tracking).
- ✅ **User Authentication** (Login, user-specific dashboards).
- ✅ **Customizable Reports** (Download project insights).

### **🤝 Contribution Guide**
1. **Fork the repository**.
2. **Create a new branch**: `git checkout -b feature-branch`
3. **Commit changes**: `git commit -m "Add feature"`
4. **Push to GitHub**: `git push origin feature-branch`
5. **Create a Pull Request**.


---

## 👨‍💻 Developed By:
- **Hemang Singh**
- [GitHub](https://github.com/Hemang14)
- [LinkedIn](https://www.linkedin.com/in/hemang14/)
