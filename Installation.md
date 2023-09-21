## Install and Run

Follow these steps to install and run the KU Polls application 
on your local development environment:

**Note**: Before you begin, ensure that you have Django installed on your system 
refer to [requirements.txt](./requirements.txt). 

1. Clone the Repository: 
    - Start by cloning the KU Polls repository to your local machine.
    ```
   git clone https://github.com/geeegrace02/ku-polls.git
    ```

2. Create a Virtual Environment:
   - Navigate to the project directory and create a virtual environment.
   ```
   cd ku-polls
   python -m venv venv
   ```
3. Activate the Virtual Environment:
   - On Windows:
   ```
   venv\Scripts\activate
   ```
   - On macOS and Linux:
   ```
    source venv/bin/activate
   ```

4. Install Dependencies: 
   - Install the necessary [requirements](./requirements.txt) dependencies.
   ```
    pip install -r requirements.txt
   ```

5. Set Values for Externalized Variables:
   -  Set and can find sample values in the provided [sample.env](./sample.env) file.

6. Run Migrations:
   - Apply database migrations to set up the database schema.
   ```
   python manage.py migrate
   ```
   
7. Install data from the data fixtures:
   ```
   python manage.py loaddata data/polls.json
   python manage.py loaddata data/users.json
   ```
   
8. Run the Application:
    ```
   python manage.py runserver
    ```
   
9. Access the Application:
   - Open your web browser and go to `http://127.0.0.1:8000/`