# KPI-Dashboard-for-H&M
H&M KPIs Project

## Project Overview

This project consists of a backend REST API, a frontend Streamlit dashboard, and a SQL database hosted on Google Cloud.

## Backend
The API is built using Flask and Flask-RESTPlus, providing a set of endpoints for user registration, login, and any other data-related operations. The backend connects to a database to store and manage user information and any other application data. It also implements a custom API key decorator to ensure that only authorized requests can access the API endpoints.

### Authentication Endpoints

/register - This endpoint is responsible for user registration. It accepts a POST request with a JSON payload containing the "username" and "password". It returns a 201 status code on successful registration, and a 400 status code if the registration fails.

/login - This endpoint is responsible for user login. It accepts a POST request with a JSON payload containing the "username" and "password". If the login is successful, it returns a 200 status code; otherwise, it returns a 400 status code.


### Datframes Endpoints

-The following endpoints are used for querying customers, transactions and article.
 
/customers to get all customers
/transactions to get all transactions
/articles to get all articles

/transactions/ageandclub to query transactions by age and club membership. It adds to transactions the columns of club_member_status and age based on customer_id and selects only the necessary columns for the filtering and api calculation

/transaction/productcategory to query transactions by product category. It adds the column of product_category to transactions based on article_id and selects only the necessary columns for the filtering and api calculation. Product_category wasn't originally in the dataframe of articles, but was created when uploading the dataframe to the mySql database. It was done by creating the new column "product_category" assigning the value "male" to Mensware and Sport articles, the value "female" to Ladiesware articles and "baby" to baby/children articles.


## Frontend
The Streamlit application serves as the user interface for the project. It communicates with the backend API to perform user registration, login, and any other necessary data-related tasks

### Main components

get_session_state(): This function returns the current Streamlit session state. Streamlit's session state allows you to store and manage variables that persist across multiple runs of the application. This is useful for managing things like user authentication status.

login(username, password) function: Allows users to login by providing username and password. This function sends a POST request to the /api/v4/login endpoint of the API, passing the provided username and password as JSON data. The 'x-api-key' header is set to the API_KEY. If user enters valid login credentials and clicks login, function sends a GET request to the backend API to authenticate the user. If authentication fails, error message is displayed.

register(username, password) function: llows new users to register by providing username and password. This function sends a POST request to the /api/v4/register endpoint of the API, passing the provided username and password as JSON data. The 'x-api-key' header is set to the API_KEY. If user registers valid details and clicks Register, function sends POST request to backend API to create a new user account. If account is successfully created, function stores the token in session state and displays success image. If registration fails, error message is displayed.

login_or_register_page(): This function is not shown in the provided code, but it renders a login or registration page in the Streamlit application. Users can either log in with their existing credentials or register for a new account.


main_app(): Displays the contents of the dashboard.py file. This is where all of the KPIs are presented.

main(): This function serves as the main entry point for the Streamlit application. It handles user authentication and displays the main application once the user is logged in. Once user is authenticated with token the main_app() is called to show the dashboard to the user

