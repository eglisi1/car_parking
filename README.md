# 🚗 Parking Space Detection Project

⚡ Find your parking spot with ease ⚡️️️

## 📷 Picture Analysis Process

This project aims to create a model that detects whether a parking space is occupied or not. It's designed for situations where a user is in front of a parking lot, presses a button, and then a camera takes a photo for analysis. The system then provides instructions on where the user should park.

```mermaid
graph TD
    A[Start: Button Pressed] -->|Triggers Camera| B[Take Photo]
    B --> C[Upload Photo]
    C --> D[Analyze Photo]
    D -->|Occupied Detection| E[Check Parking Availability]
    E -->|If Occupied| F[Find Next Available Space]
    E -->|If Not Occupied| G[Direct to Current Space]
    F --> H[Provide Parking Instructions]
    G --> H
    H --> I[End: User Parks]
```

## ⚙️ Project Structure

Thanks to [Cookie Cutter](https://drivendata.github.io/cookiecutter-data-science/)

## 🛠️ Setup and Installation

To set up this project:

1. Clone the repository.
2. Install dependencies using ```pip install -r requirements.txt``` from the root directory.
3. (If you're on a RaspberryPI run ```pip install -r pi_requirements.txt```. This won't work on Windows!)
4. Start the app with uvicorn ```uvicorn main:app --reload``` from the src/backend directory.
5. Profit 💰

## 🐍 Python Version

This project is built with Python 3.11.1.
