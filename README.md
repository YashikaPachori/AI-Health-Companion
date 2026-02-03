# AI-Health-Companion
# 🏥 Medicate – AI Health Companion

Medicate is an AI-powered health companion that helps users understand their symptoms, receive early health guidance, and consult doctors when required. The system focuses on providing symptom-based disease prediction along with actionable medical recommendations.

---

## 📌 Problem Statement

Many people experience health symptoms but are unsure about their seriousness. Lack of immediate medical guidance often leads to delayed treatment, unnecessary panic, or avoidable doctor visits. There is a need for an intelligent and personalized system that can provide early health insights and guide users toward timely medical consultation.

---

## 🎯 Project Objectives

- Predict possible diseases based on user-entered symptoms  
- Provide early healthcare guidance and recommendations  
- Help users decide when to consult a doctor  
- Bridge the gap between patients and healthcare services using AI  

---

## ⚙️ Key Features

- 🔍 Symptom-based disease prediction  
- 📊 Confidence score for predictions  
- 💡 Health recommendations:
  - Precautions
  - Diet suggestions
  - Exercise guidance
  - Medicine information
- 👨‍⚕️ Doctor consultation and appointment booking
- 🧑‍💻 Separate roles for Patient, Doctor, and Admin
- 📜 Prediction history tracking
- ⚠️ Emergency guidance and medical disclaimer

---

## 🧠 Technology Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Machine Learning:** SVM-based classification (basic)
- **Tools:** VS Code, GitHub, GitHub Desktop

---

## 🛠️ How the System Works

1. User selects symptoms from the interface  
2. The system analyzes symptoms using AI + rule-based logic  
3. A possible disease is predicted with a confidence score  
4. Health recommendations are displayed  
5. User can consult a doctor or book an appointment if needed  

---

## ⚠️ Important Disclaimer

This system **does not replace professional medical advice**.  
In case of severe, emergency, or life-threatening conditions, users are strongly advised to consult a qualified doctor or visit the nearest hospital immediately.

---

## 🚀 Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/medicate.git
   
2. Navigate to the project directory:

cd medicate

3.Create and activate virtual environment:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

4.Install dependencies:

pip install django pillow

5.Run migrations:

python manage.py migrate

6.Start the server:

python manage.py runserver

7.Open browser and visit:

http://127.0.0.1:8000/

📈 Future Enhancements

Medicine reminder system

Video consultation feature

Mobile application

Advanced ML models with real datasets

Emergency alerts integration

👥 Team

Team Leader: Yashika Pachori

Project Type: Academic / College Project

🏁 Conclusion

Medicate aims to provide early health awareness, reduce confusion around symptoms, and encourage responsible healthcare decisions through intelligent technology and doctor consultation.
