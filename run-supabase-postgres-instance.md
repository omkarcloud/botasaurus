### How to create a PostgreSQL database on Supabase?

1. First, visit [supabase.com](https://supabase.com/dashboard/sign-in?) and sign up using your GitHub account.
![supabase-sign-up](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/supabase-sign-up.png)

2. Once signed up, click on the "New project" button.
![New supabase Project](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/new-supabase-project.png)

3. Enter the following settings, then click the "Create New Project" button:
```yaml
Name: Pikachu # Choose any name
Database Password: greyninja1234_A # For testing, use "greyninja1234_A". In production, use a strong password.
Region: West US (North California) # Select the region closest to your server for best performance.
```
![Enter supabase Settings](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/enter-supabase-settings.png)

4. Wait a few minutes for the project to be created.
![wait project](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/wait-project.png)

5. Navigate to "Project settings" > "Database" and copy the connection string.
![connection string](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/connection-string.png)

6. In Vscode, create a new file `main.py` and paste the following code to test the connection:
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a database connection URL
db_url = 'SUPABASE_CONNECTION_STRING'
engine = create_engine(db_url.replace("postgres://", "postgresql://", 1))
Session = sessionmaker(bind=engine)
session = Session()

# Define a model
Base = declarative_base()
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Create the table
Base.metadata.create_all(engine)

# Insert a record
new_user = User(name='John Doe')
session.add(new_user)
session.commit()

# Query records
users = session.query(User).all()
for user in users:
    print(user.id, user.name)

# Print a success message
print("Hurray! database connection is working.")
```

7. In the pasted code:
    - Replace `SUPABASE_CONNECTION_STRING` with the connection string you copied from the Supabase dashboard.
    - In the connection string, replace `[YOUR-PASSWORD]` with the password you set when creating the instance (e.g., `greyninja1234_A`).

8. Run the code. You should see the following output:
```
1 John Doe
Hurray! database connection is working.
```
![supa Output](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/supa-output.png)

10. Finally, to use the PostgreSQL database in Botasaurus:
    - Open the `backend/scrapers.py` file.
    - Add the following line, replacing `SUPABASE_CONNECTION_STRING` with your connection string:
    ```py
    Server.set_database_url('SUPABASE_CONNECTION_STRING')
    ```
    ![Use in Botasaurus supa](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/use-in-botasaurus-supa.png)

## How to delete the Supabase project?
Deleting the project will permanently erase all data associated with it. Make sure to download any important data before proceeding. 

To delete the project, go to "Project settings" > "General" and click on the "Delete Project" button.
![Delete supabase](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/delete-supabase.png)