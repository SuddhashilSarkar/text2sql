# text2sql

An AI-powered tool that converts natural language into SQL queries. It enables users to interact with databases using simple text prompts, automatically generating the corresponding SQL queries, making database interaction intuitive and accessible for both technical and non-technical users.

## Setup Instructions

### Prerequisites

Ensure you have the following installed before running the setup script:

- Python 3.7+ (Check with `python --version` or `python3 --version`)
- Git (Optional, but recommended for version control)

### Installation Steps

1. **Clone the Repository**
   ```sh
   git clone https://github.com/SuddhashilSarkar/text2sql.git
   cd text2sql
   ```

2. **Run the Setup Script**
   ```sh
   python setup.py
   ```
   This script will:
   - Create a virtual environment (`venv`).
   - Activate the virtual environment.
   - Install dependencies from `requirements.txt`.

3. **Activate the Virtual Environment (If Not Automatically Activated)**

   - **Windows (CMD/PowerShell)**:
     ```sh
     venv\Scripts\activate
     ```

   - **Mac/Linux**:
     ```sh
     source venv/bin/activate
     ```

4. **Run the Application**
   ```sh
   python main.py
   ```
   (Replace `main.py` with the actual entry point of your application.)

5. **Deactivate the Virtual Environment**
   ```sh
   deactivate
   ```
   


## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Added new feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.
