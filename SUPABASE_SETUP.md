# Supabase Integration Setup Guide

## Issue Resolution

If you're getting the error: **"[Errno -2] Name or service not known"**

This means the Supabase credentials are either:
1. Not configured (placeholder values)
2. The Supabase URL is incorrect
3. There's a network connectivity issue

## Two Options

### Option 1: Use Supabase (Recommended for Production)

#### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Create a new project
4. Wait for the project to be ready

#### Step 2: Get Your Credentials
1. In your Supabase dashboard, go to **Settings > API**
2. Copy your **Project URL** (looks like: `https://xxxxx.supabase.co`)
3. Copy your **anon public** key

#### Step 3: Create the Registration Table
In Supabase SQL Editor, run this query:

```sql
CREATE TABLE registration (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  email text UNIQUE NOT NULL,
  password text NOT NULL,
  created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
```

#### Step 4: Update .env File
Edit the `.env` file in your project root:

```
SUPABASE_URL=https://your-actual-project.supabase.co
SUPABASE_KEY=your-actual-anon-key
```

#### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 6: Run the App
```bash
python app.py
```

---

### Option 2: Use MySQL Only (Current Setup)

If you don't have Supabase configured, the app will **automatically fall back to MySQL** for authentication.

Make sure:
1. MySQL is running on `localhost`
2. Credentials in `app.py` are correct:
   - host: `localhost`
   - user: `root`
   - password: `root`
   - database: `rohitproject`

Just run:
```bash
python app.py
```

---

## How the System Works

- **Supabase Configured**: Uses Supabase for the "registration" table
- **Supabase Not Configured**: Automatically falls back to MySQL
- **Supabase Connection Error**: Automatically falls back to MySQL

The app logs informative messages on startup showing which system is being used.

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `[Errno -2] Name or service not known` | Invalid/placeholder Supabase URL | Update `.env` with correct credentials |
| `Connection refused to MySQL` | MySQL not running | Start MySQL service |
| `Table not found (registration)` | Supabase table doesn't exist | Run the SQL query above in Supabase |
| `Authentication error` | Wrong Supabase credentials | Double-check `.env` values |

---

## Security Notes

⚠️ **Important**: 
- Never commit `.env` file with real credentials to public repositories
- Use Supabase RLS (Row Level Security) policies in production
- Hash passwords using bcrypt (consider upgrading for production)

