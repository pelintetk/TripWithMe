# TripWithMe

## Project Description

The idea for TripWithMe came from my own travel experiences. Whenever I travel, I need help remembering the essential things I should pack. After learning web development through CS50W, I realized that I could build a website to solve this problem.

TripWithMe helps users prepare for their trips with a checklist of essential items. Users can create different types of trips, and international trips include additional checklist items, such as a passport and other travel essentials.

I also wanted to make it easier to track my spending while traveling. I usually take notes about what I spend money on, so I added a feature that allows users to record their expenses, track their budget, and see how much money they have spent.

Another reason I created TripWithMe is that I enjoy sharing my travel experiences and recommending places to people I love. Sometimes, especially when traveling abroad, it can be difficult to remember the names of places I have visited. With TripWithMe, users can save places they have visited, rate them, and write reviews to remember their experiences. They can also save places they want to visit in the future.

My goal was to create a website that brings these useful travel-planning features together in one place and makes traveling more organized and enjoyable.

## Distinctiveness and Complexity

I have never personally come across a website quite like TripWithMe. What makes TripWithMe special to me is that it works like a personal travel notebook, but with more interactive features. People often enjoy looking back at their trips and remembering what they did, where they went, and how much they spent. I wanted to bring all these things together in one website.

TripWithMe is more than a simple travel checklist. It combines trip planning, expense tracking, budget management, place discovery, and personal reviews. Users can organize their travel information and keep a record of their experiences in one place.

One of the biggest challenges I faced during development was working with APIs. As a student, I wanted to use free services, but finding suitable APIs was difficult. In particular, retrieving photos for places was challenging. Although I integrated Wikimedia Commons to improve photo availability, some places still do not have photos. However, users can still see the place names and other available information.

Another challenging part was automated testing and integrating the tests with GitHub Actions. I experienced some difficulties while setting up the workflow and making sure the tests ran successfully. Eventually, I was able to create 50 automated tests and run them through GitHub Actions.

Most of the other features were developed using the knowledge I gained from CS50W. This project helped me bring together what I learned about Django, databases, JavaScript, and web development while also learning how to solve problems that appeared during the development process.

## Features

- **User Authentication:** Users can register, log in, and manage their own trips.
- **Trip Management:** Users can create and delete domestic or international trips.
- **Travel Checklist:** Each trip has an automatically generated checklist. Users can add their own items and mark them as completed.
- **Expense Tracking:** Users can record their expenses, select categories, and see how much money they have spent.
- **Budget Management:** Users can set a budget and track their remaining balance.
- **Place Discovery:** Users can explore restaurants, cafés, attractions, and shopping places using the Geoapify API.
- **Place Photos:** The website uses Wikimedia Commons to provide photos for some places.
- **Saved Places:** Users can save places they want to visit and mark them as visited.
- **Ratings and Reviews:** Users can rate and review places they have visited.
- **Responsive Design:** The website can be used on both desktop and mobile screens.

## File Structure

- **`models.py`:** This file contains the database models, such as Trip, Expense, Place, and ChecklistItem. When we make changes to the models, we use the `makemigrations` and `migrate` commands to update the database structure.

- **`views.py`:** This file handles user requests and contains the logic behind features such as creating trips, adding expenses, and managing places.

- **`urls.py`:** This file connects URL paths to the corresponding views, allowing users to navigate between different pages of the website.

- **`templates/`:** This folder contains the HTML templates that define the user interface. For example, `create_trip.html` and `login.html` display the trip creation and login pages.

- **`photo_service.py`:** This file communicates with Wikimedia Commons to search for photos of places and retrieve their information.

- **`management/commands/find_place_photos.py`:** This file contains a Django management command that displays photo options, allows me to select the most suitable photo, and saves the selected photo information to the database.

- **`tests.py` / Test Files:** These files contain automated tests that check whether different features of the website work correctly.

- **`.github/workflows/tests.yml`:** This file defines the GitHub Actions workflow, which automatically runs the project's tests when code is pushed to GitHub or a pull request is created.

## How to Run

To run TripWithMe on your own computer, follow these steps:

**1. Download the project**

Clone the repository from GitHub:

```bash
git clone https://github.com/pelintetk/TripWithMe.git
cd TripWithMe
```

**2. Install Python and create a virtual environment**

Make sure Python is installed on your computer. Then create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment depending on your operating system and terminal.

**Windows (Git Bash):**

```bash
source venv/Scripts/activate
```

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

Once the virtual environment is activated, you can continue installing the required packages.

**3. Install the required packages**

Install the project's dependencies using:

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the main project directory and add the required environment variables:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
GEOAPIFY_API_KEY=your-geoapify-api-key
```

The Geoapify API key can be obtained from the Geoapify website. The `.env` file should not be uploaded to GitHub because it contains private information.

**5. Set up the database**

Run the following command to apply the database migrations:

```bash
python manage.py migrate
```

**6. Start the server**

Run:

```bash
python manage.py runserver
```

After starting the server, open the following address in your browser:

http://127.0.0.1:8000/

TripWithMe is now ready to use. You can register an account and start planning your trips.

## Additional Information
## External APIs

In this project, I used the Geoapify and Wikimedia Commons APIs. Geoapify helps users discover places, while Wikimedia Commons is used to search for photos of those places.

## Testing and Continuous Integration

While developing TripWithMe, I tried to consider different situations and possible errors that users might encounter. For example, entering text such as "abc" into a budget field instead of a number should result in a validation error.

I added automated tests because I wanted to make the website more reliable and prevent problems for users.

The project includes 50 automated tests that check different parts of the application.

I learned about Continuous Integration (CI) during CS50W and decided to apply what I learned to my own project. I integrated GitHub Actions into TripWithMe to automate the testing process. This made development easier because, whenever I push changes to GitHub, the tests run automatically. It also helps me identify potential problems and make sure that new changes do not break existing features.
To run the tests locally, use:

```bash
python manage.py test
```