# BandSync

BandSync is a web and mobile-friendly app to help brass bands (and other groups) schedule events, track attendance, and manage their organization.

## Features
- User registration & login (JWT-based)
- Role-based access: Admins and Members
- Event creation, editing, deleting (Admins only)
- RSVP options (Yes, No, Maybe)
- Dashboard for each user showing upcoming events
- Admin dashboard with org settings and user management
- Responsive, mobile-first frontend (PWA enabled)

## Project Structure
```
BandSync/
│
├── backend/        # Flask API backend
├── frontend/       # React frontend
├── .env            # Environment variables
├── README.md       # This file
└── seed_data.sql   # SQL for test data
```

## Backend Setup
1. `cd backend`
2. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up PostgreSQL and create a database/user matching `.env`.
5. Run migrations (or create tables):
   ```
   flask shell
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```
6. (Optional) Seed test data:
   ```
   psql $DATABASE_URL -f ../seed_data.sql
   ```
7. Run the backend:
   ```
   flask run
   ```

## Frontend Setup
1. `cd frontend`
2. Install dependencies:
   ```
   npm install
   ```
3. Start the frontend:
   ```
   npm start
   ```

## Deployment (Render)
- Add environment variables from `.env` in Render dashboard for both web services.
- Set up build/start commands for backend and frontend as needed.

## .env Example
See `.env` in the root for required variables.

---

For more details, see code comments and each folder's README (if present).
