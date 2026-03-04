# LeadFlow AI – Complete Setup Guide (Supabase + Render)

---

## Step 1 – Supabase Database Setup (5 minutes)

1. Go to **supabase.com** → Sign up free → New Project
2. Choose a name (e.g. `leadflow`) and set a strong DB password → save it!
3. Wait ~2 min for project to spin up
4. Go to **SQL Editor** (left sidebar) → click **New Query** → paste and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

5. Go to **Project Settings → Database → Connection String → URI**
   - Copy the URI — it looks like:
     `postgresql://postgres:[YOUR-PASSWORD]@db.abcdefgh.supabase.co:5432/postgres`
   - Replace `[YOUR-PASSWORD]` with your actual password

---

## Step 2 – Local Setup

```bash
# 1. Unzip the project and cd into it
cd leadflow_rag

# 2. Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux

# 5. Edit .env — paste your Supabase DATABASE_URL and OpenAI key
notepad .env                  # Windows
nano .env                     # Mac/Linux
```

Your `.env` should look like:
```
DATABASE_URL=postgresql://postgres:mypassword@db.abcdefgh.supabase.co:5432/postgres
DEBUG=True
SECRET_KEY=any-long-random-string-here
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=sk-...
```

```bash
# 6. Run migrations (creates all tables in Supabase)
python manage.py migrate

# 7. Create superuser (for Django admin)
python manage.py createsuperuser

# 8. Seed sample data (optional but recommended)
python manage.py seed_sample_data

# 9. Run the server
python manage.py runserver
```

Open: http://localhost:8000

---

## Step 3 – Deploy to Render (10 minutes)

1. Push your code to GitHub (create a new repo)

2. Go to **render.com** → New → Web Service → Connect your GitHub repo

3. Configure:
   - **Name:** leadflow-rag
   - **Environment:** Python
   - **Build Command:**
     ```
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```
     gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
     ```

4. Add Environment Variables in Render dashboard:

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | your Supabase URI |
   | `SECRET_KEY` | any long random string |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
   | `OPENAI_API_KEY` | your OpenAI key |

5. Click **Deploy** — done! 🎉

---

## Troubleshooting

**`psycopg2` install error on Windows:**
```bash
pip install psycopg2-binary --only-binary=:all:
pip install -r requirements.txt
```

**`pgvector` extension error:**
Make sure you ran `CREATE EXTENSION IF NOT EXISTS vector;` in Supabase SQL Editor.

**`relation does not exist` error:**
Run `python manage.py migrate` again.

**Static files not loading on Render:**
Make sure `DEBUG=False` and `ALLOWED_HOSTS` includes your Render domain.
