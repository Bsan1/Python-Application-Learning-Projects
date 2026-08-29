CNG445 - Assignment 3: A Local Event Advertisement Portal

 Team Members
1. Name: Emmanuel Monye       
2. Name:  BARIŞ ŞAN      


System Details
* Python Version: Python  3.9.6 
* Operating System:  Windows 10 / macOS catalina


Teamwork & Task Distribution
We divided the project into two main functional areas to ensure we could work in parallel without conflicts. We communicated regularly via [ e.g., Discord/WhatsApp ] and used [ e.g., GitHub/Google Drive ] to share code.

 [ BARIŞ ] was responsible for:
    - User Authentication (Login, Logout, Session Management).
    - User Registration (including Password Validation and Admin detection).
    - User Profile Management (Edit details).
    - Admin functionalities (Manage Societies).
    - Base HTML/CSS Template structure.

 [ Emmanuel ] was responsible for:
    - Event Management (Announce Event form, Fee validation).
    - Managing "My Events" (List and Delete functionality).
    - Search Functionality (Keyword search, Categorization by Society).
    - Event Details page ("See More").
    - Database Schema Design (Entity relationships).

** Testing Strategy: **
We tested our individual components locally using the Flask development server. Once features were complete, we merged our code and performed integration testing to ensure the Search function correctly retrieved events created by the Event Manager, and that Admin restrictions correctly blocked unauthorized access to specific routes.


Web Deployment
The website is deployed and accessible at the following URL:

metuleap.pythonanywhere.com




