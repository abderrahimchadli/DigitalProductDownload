# DigitalProductDownload  

**Developer**: Abderrahim Chadli  

DigitalProductDownload is a Python-based application designed to manage the distribution of digital products. It provides functionalities for user authentication, product management, and secure delivery of digital goods.  

## Features  

- **User Authentication**: Secure user registration and login system.  
- **Product Management**: Tools to add, update, and manage digital products.  
- **Order Processing**: Efficient handling of product orders and downloads.  

## Project Structure  

The repository is organized as follows:  

- `auth_app/`: Contains modules related to user authentication.  
- `products/`: Manages product-related functionalities.  
- `project/`: Core project configurations and settings.  
- `static/assets/`: Stores static files like images, CSS, and JavaScript.  
- `Lib/` and `Scripts/`: Virtual environment directories for dependencies.  
- `manage.py`: Django's command-line utility for administrative tasks.  
- `requirements.txt`: Lists the Python dependencies for the project.  

## Installation  

To set up the project locally:  

1. **Clone the repository**:  

   ```bash
   git clone https://github.com/abderrahimchadli/DigitalProductDownload.git
   cd DigitalProductDownload
   ```  

2. **Set up a virtual environment**:  

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```  

3. **Install dependencies**:  

   ```bash
   pip install -r requirements.txt
   ```  

4. **Apply migrations**:  

   ```bash
   python manage.py migrate
   ```  

5. **Run the development server**:  

   ```bash
   python manage.py runserver
   ```  

   Access the application at `http://127.0.0.1:8000/`.  

## Usage  

- **User Registration**: Navigate to the registration page to create a new account.  
- **Product Listing**: Browse available digital products.  
- **Purchase and Download**: Add products to your cart, proceed to checkout, and download purchased items.  

## Contributing  

Contributions are welcome! Please fork the repository and submit a pull request with your proposed changes.  

## License  

This project is licensed under the MIT License. See the `LICENSE` file for details.  
Abderrahim Chadli
---
