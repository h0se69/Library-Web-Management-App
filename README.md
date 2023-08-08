
# CS157A Project (Summer 2023): Library Web Management Application

A Library Web Management Application that will enable users to check out books, reserve ‘out of stock’ books, return books at the assigned due date, create a read-later list to keep track of future books they may want to read.

A **3-tier** Client-Server application architecture\
&emsp;&emsp;&emsp; **Tier 1**: Client: HTML\
&emsp;&emsp;&emsp; **Tier 2** Application Server & Middleware: Python & JavaScript\
&emsp;&emsp;&emsp; **Tier 3** Data Server: MySQL





## Deployment

To run this application you need:

[MySQL](https://www.mysql.com/downloads/)

[MySQL Workbench](https://www.mysql.com/products/workbench/)

[Python 3.8.0](https://www.python.org/downloads/release/python-380/)

[Install PIP](https://pip.pypa.io/en/stable/cli/pip_install/)

[Clone/Download this repo](https://github.com/h0se69/CS157A-Project)


Install the requirements.txt --> Python libraries used
```bash
pip install -r requirements.txt
```

Ensure you set up the [Environment Variables] & have a Google Book API Key [FAQ]

Start the application:

```bash
Windows: py run.app
Mac: python3 run.app
```




## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`MY_SQL_HOST`\
`MY_SQL_USER`\
`MY_SQL_PASSWORD`\
`MY_SQL_SCHEMA_NAME`\
`GOOGLE_BOOKS_API_KEY`

## FAQ

#### Why can't I add books to the Database?

You need to make sure you are using the admin account and have a Google Book API Key

#### How do I get a Google Book API Key?

1) Open the [Credentials page](https://console.cloud.google.com/apis/credentials) in the API Console.
2) The API supports several types of restrictions on API keys. If the API key that you need doesn't already exist, then create an API key in the Console by clicking [Create credentials](https://console.cloud.google.com/apis/credentials)  > API key. You can restrict the key before using it in production by clicking Restrict key and selecting one of the Restrictions.
3) [More Information Here](https://developers.google.com/books/docs/v1/using)

#### What are the admin account credentials?
    ADMIN EMAIL AND PASSWORD USE THIS WHEN LOGGING IN
        email: cs157A@admin.com
        password: password

#### I can't connect to the Database?
Ensure you followed the [Deployment](#Deployment) steps \
Make sure your `.env` file is updated to match your MySQL Workbench settings (Host, User, Password, SchemaName)

#### Other question or issues?
Open a PR/Issue we are happy to help




## Demo

[Video](https://www.dropbox.com/scl/fi/emqump752vfglx37iuwv4/2023-08-06-15-14-56_trimmed.mkv?dl=0&rlkey=hf3cbcexf7lxx6k8lz7wiyb8m)
## Division of Work
**Jose Jr. Betancourt Huizar**:
```bash
Database Models (MySQL): User, UserActivity, BookRatings, Books, Read-Later

EER Diagram

Frontend (HTML): ViewBooks, UserProfile, SpecificBook, SearchByCategory, RegisterPage, LoginPage, Navbar, BestSellers, AddBook

API Routes(Backend): register, login, logout, user_profile_page, best_sellers_page, all_books_page,
search_by_category_page, search_books_api, request_google_books_api, add_to_read_later_api, add_book_rating_api, remove_read_later_api

Final Project Report: Description, Goals, Application/Functional Requirements & Architecture, ER Data Model + Relational Schema,
Implementation Details, Demonstration, Conclusion
```

**Anton Bogatyrev**:
```bash
Database Models(MySQL): Checkout, Return, Books

EER Diagram

Frontend (HTML): ViewBooks, LibrarianView, AdvancedSearch

API Routes(Backend): advanced_search_page, search_books_api, librarian_view_page, return_book_api, checkout_book_api, add_fine_api, get_book_api

Final Project Report: Description, Goals, Application/Functional Requirements & Architecture, ER Data Model + Relational Schema, 
Major Design Decisions, Demonstration, Conclusion
```
