# Weather Data Collection System

## Overview
This project is a simple tool designed to fetch real-time weather data for specified cities using the [OpenWeatherMap API](https://openweathermap.org/api). 

The system performs the following actions:
1. **Fetches Weather Data**: Gets current temperature, humidity, and weather conditions for cities listed in your configuration.
2. **Displays Output**: Shows the weather details directly in your terminal.
3. **Cloud Storage**: Uploads the raw data to an **AWS S3** bucket for long-term storage or analysis.
4. **Local Backup**: Saves a copy of the weather data as a `.json` file in a local `docs/` folder.

This project demonstrates core DevOps and engineering concepts including API integration, cloud storage (S3), environment management, and file handling.

---

## Prerequisites
Before you run this project, ensure you have the following:

1. **Python 3.x** installed on your system.
2. An **OpenWeatherMap API Key**.
3. **AWS Credentials** configured (if using S3 features).

---

## Setup Instructions

### 1. Initialize the Environment
First, create a virtual environment to manage dependencies so they don't interfere with other projects.

```powershell
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On Windows (Git Bash / PowerShell):
./venv/Scripts/activate
```

### 2. Install Dependencies
Install the required Python libraries (boto3, requests, python-dotenv).

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory to store your secrets. It should look like this:

```ini
OPENWEATHER_API_KEY=your_api_key_here
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your_unique_bucket_name
CITIES=London,Anantapur,Hyderabad,New York
```

---

## Running the Application

To run the weather collector, use the following command from the project root:

```powershell
python src/main.py
```

*Note: If you are running strictly from the virtual environment without activating it first, you can also use:*
```powershell
./venv/Scripts/python src/main.py
```

---

## Infrastructure Management (Terraform)
This project uses **Terraform** to manage the AWS infrastructure (S3 bucket).

### 1. Initialize Terraform
Initialize the working directory containing Terraform configuration files. This downloads necessary plugins.
```powershell
cd infra
terraform init
```

### 2. View Execution Plan
Preview the changes that Terraform will make to your infrastructure.
```powershell
terraform plan
```

### 3. Apply Changes
Create or update the infrastructure resources on AWS.
```powershell
terraform apply
```
*Type `yes` when prompted to confirm.*


---

## Expected Output

### 1. Terminal Output
When the script runs successfully, you will see logs indicating the data fetch and save status:

```text
[INFO] Fetching weather for London...
[INFO] London: 56.62°F, 86% humidity, broken clouds
[INFO] Uploaded data for London to s3://weather-data-project/weather-data/London/London_20251209T155741Z.json
[INFO] Saved data for London to docs\London_20251209T155741Z.json
```

### 2. Local Files
Check the `docs/` folder in your project directory. You will see new JSON files created for each city:

**Example File:** `docs/London_20251209T155741Z.json`
```json
{
    "city": "London",
    "temperature_f": 56.62,
    "humidity": 86,
    "condition": "broken clouds",
    "timestamp": "2025-12-09T15:57:41.341947+00:00",
    "raw": { ... }
}
```

### 3. S3 Bucket
If AWS is configured, the same JSON file is uploaded to your S3 bucket under the `weather-data/` folder.

---

## Project Structure
```
weather-data-collector/
├── docs/                   # Local folder where weather JSON output is saved
├── infra/
│   ├── main.tf             # Terraform resources
│   ├── outputs.tf          # Terraform outputs
│   └── variables.tf        # Terraform variables
├── src/
│   └── main.py             # Main application logic
├── .env                    # Environment variables (API keys, config)
├── .gitignore              # Files to ignore in Git
├── README.md               # This documentation
└── requirements.txt        # Python dependencies
```

---

## Conclusion
This project successfully integrates external APIs, cloud storage, and local file handling into a cohesive Python application. It serves as a practical example of:
- **Automation**: Regularly fetching and storing data without manual intervention.
- **Resilience**: Handling errors gracefully (e.g., if one city fails or S3 is unreachable).
- **Organization**: structuring code and output in a clean, maintainable way.

Feel free to extend this project by adding more cities, visualizing the data, or deploying it as a Lambda function!
