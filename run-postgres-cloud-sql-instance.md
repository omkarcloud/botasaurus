### How to create a PostgreSQL database on Google Cloud?

1. If you don't already have one, create a Google Cloud Account. You'll receive a $300 credit to use over 3 months.
   ![Select-your-billing-country](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/Select-your-billing-country.png)

2. Visit [this link](https://console.cloud.google.com/sql/instances) and click on the "Create Instance" button.
   ![Create Instance](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/create-pg-instance.png)

3. Choose PostgreSQL as your database engine.
   ![Select PostgreSQL](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/select-postgres.png)

4. Enter the following settings, **BUT DO NOT AND YES DO NOT** click the "Create Instance" button **YET!** (We'll do that after the next step.)
   ```
   Instance ID: pikachu # Choose any name for your instance.
   Password: pikachu # For testing purposes, we're using a simple password "pikachu". In a production environment, use a strong password.
   Choose a Cloud SQL edition: Enterprise # Opt for the Enterprise edition as it is cheaper.
   Preset for this edition: Sandbox # Select the Sandbox preset as it is also cheaper.
   Region: us-central1 # For testing, we're using the default region. In production, select the region that is closest to your server for best performance.
   Machine shapes: Shared Core/1 vCPU, 0.614 GB # Choose the cheapest instance as we don't need a high-end machine for storing web scraping data.
   Storage Capacity: 10 GB
   Enable automatic storage increases: Yes # Enable this feature so you don't have to worry about running out of storage. (Awesome feature!)
   Enable deletion protection: No # Disable this feature, otherwise you'll need to change this setting later to delete the instance.
   ```
   ![Enter Settings](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/enter-settings.png)

5. In the "Connections" > "Authorized Network" tab:
   - Click "Add Network"
   - Enter "0.0.0.0/0" to allow access from any IP (for testing only; in production, add your region's CIDR which you can find [here](https://www.gstatic.com/ipranges/cloud.json))

   ![Add Network](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/add-network.png)

6. Click the "Create Instance" button now. The instance creation will take approximately 20 minutes.
   ![Create Instance](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/create-instance.png)

7. In Vscode, create a new file `main.py` and paste the following code to test the connection:
    ```python
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    # Create a database connection URL
    db_url = 'postgresql://postgres:PASSWORD@IP_ADDRESS:5432/postgres'
    engine = create_engine(db_url)
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
8. In the pasted code:
   - Replace `PASSWORD` with the password you set when creating the instance (like, `pikachu`)
   - Replace `IP_ADDRESS` with the instance's IP address, which you can find in the [Cloud SQL instance page](https://console.cloud.google.com/sql/instances)

   ![IP Address](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/ip-address.png)

9. Run the code. You should see the following output:
   ```
   1 John Doe
   Hurray! database connection is working.
   ```
   ![Output](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/output.png)

10. Finally, to use the PostgreSQL database in Botasaurus:
    - Open the `backend/scrapers.py` file
    - Add the following line, replacing `PASSWORD` and `IP_ADDRESS` with your values:
      ```py
      Server.set_database_url('postgresql://postgres:PASSWORD@IP_ADDRESS:5432/postgres')
      ```
   ![Use in Botasaurus](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/use-in-botasaurus.png)


## How to delete the PostgreSQL database and avoid incurring charges?

Deleting the instance will permanently erase all data associated with it. Make sure to download any important data before proceeding.

To delete the instance, go to the [Google Cloud SQL Instances page](https://console.cloud.google.com/sql/instances) and delete the instance.
![Delete instance](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/delete-instance.gif)

After deleting the instance, you will not incur any further charges.