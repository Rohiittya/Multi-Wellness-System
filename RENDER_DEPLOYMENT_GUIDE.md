# Render Deployment Guide

## Prerequisites
- Render account (https://render.com)
- MySQL database (on Render or external)
- GitHub repository

## Step 1: Set Up MySQL Database on Render

### Option A: Use Render's MySQL (Recommended)
1. Go to Render Dashboard
2. Click "New +" → "MySQL"
3. Fill in the details:
   - **Name**: `multi-wellness-db`
   - **Database**: `rohitproject`
   - **User**: Choose your username
   - **Region**: Select your region
4. Click "Create Database"
5. Copy the connection details (Internal Database URL)

### Option B: Use External MySQL (e.g., AWS RDS, DigitalOcean)
1. Create a MySQL database on your chosen provider
2. Get the connection details: host, user, password, database name

## Step 2: Deploy Flask App on Render

1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository (Multi-Wellness-System)
4. Fill in the details:
   - **Name**: `multi-wellness-system`
   - **Region**: Same as your database
   - **Branch**: `master`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free (or Paid if needed)

## Step 3: Add Environment Variables

In your Render Web Service settings, go to **Environment** and add:

```
DB_HOST=your-render-database-host.onrender.com
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_NAME=rohitproject
DB_PORT=3306
```

**To find your database details:**
1. Go to your MySQL service on Render
2. Copy the "Internal Database URL" (looks like: `mysql://user:password@host:port/database`)
3. Extract:
   - `user` → `DB_USER`
   - `password` → `DB_PASSWORD`
   - `host` → `DB_HOST`
   - `database` → `DB_NAME`
   - `port` (usually 3306) → `DB_PORT`

## Step 4: Verify Deployment

1. Click "Deploy" on your web service
2. Wait for the build to complete
3. Check the logs for any errors
4. Once deployed, your app URL will be something like: `https://multi-wellness-system.onrender.com`

## Troubleshooting

### "Can't connect to MySQL server" Error
- Check that DB_HOST, DB_USER, DB_PASSWORD, DB_NAME are correctly set
- Make sure your Render database is in the same region as your web service
- Verify the database credentials are correct

### Database Connection Timeout
- Your web service and database must be able to communicate
- If using external MySQL, ensure Render's IP is whitelisted
- Check your firewall/security group settings

### Tables Not Creating
- The app will automatically create `users` and `login_logs` tables on first run
- If they don't appear, check the logs for SQL errors

## Local Development

For local testing, ensure your `.env` file has:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=rohitproject
DB_PORT=3306
```

Then run:
```bash
python app.py
```

## Security Notes

⚠️ **Never commit `.env` to GitHub!** 
- Add `.env` to `.gitignore`
- Use Render's environment variables for sensitive data
- Change the default MySQL password after creating the database

## Support

For issues:
1. Check Render logs: Dashboard → Web Service → Logs
2. Verify environment variables are set correctly
3. Test database connection separately if needed
