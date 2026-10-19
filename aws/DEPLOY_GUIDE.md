# AgroNex-Pi: AWS Cloud Deployment Guide (Student Free Tier)

This guide walks you step-by-step through deploying the cloud backend and remote dashboard on AWS. The setup runs **100% within the AWS Free Tier** (Lambda offers 1M free requests/month, API Gateway offers 1M free requests/month, and S3 offers 5GB free storage).

---

## 🏛️ System Architecture

```
[ Raspberry Pi 4B (AgroNex-Pi) ]
   │
   ├─► Background AWSRelay Thread ───► POST /telemetry ──┐
   ├─► Camera Auto-Scan (Green HSV) ──► POST /scan ──────┤
   └─◄ Polling Remote Commands ─────── GET  /command ────┤
                                                         │
                                               [ AWS API Gateway (HTTP API) ]
                                                         │
                                               [ AWS Lambda Function ]
                                                 (lambda_function.py)
                                                         │
                                               [ Amazon S3 Bucket ]
                                                 (agronex-pi-data)
                                                 ├─ state.json
                                                 ├─ scans_log.json
                                                 ├─ scans/scan_xxx.jpg
                                                 └─ pending_command.json
                                                         ▲
                                                         │
[ Remote Dashboard (Any Phone / Laptop) ] ───────────────┘
  (index.html hosted on S3 or opened via browser URL)
```

---

## 📦 Prerequisites

1. An **AWS Account** (Free Tier or AWS Academy / Student account).
2. Preferred region: `ap-south-1` (Mumbai) or `us-east-1` (N. Virginia).

---

## Step 1: Create the S3 Storage Bucket

1. Sign in to the [AWS Management Console](https://console.aws.amazon.com/).
2. In the top search bar, type **S3** and open it.
3. Click **Create bucket**:
   - **Bucket name**: `agronex-pi-data-<your-name>` (e.g. `agronex-pi-data-nikhil`). Bucket names must be globally unique.
   - **AWS Region**: Select `ap-south-1` (Asia Pacific - Mumbai) or your closest region.
   - **Block Public Access settings**:
     - *Uncheck* "Block all public access" (and check the acknowledge box below it) so that disease scan images and dashboard assets can be viewed in browsers.
   - Leave other settings as default and click **Create bucket**.

4. **Add CORS Policy to S3**:
   - Click on your newly created bucket.
   - Go to the **Permissions** tab.
   - Scroll down to **Cross-origin resource sharing (CORS)** and click **Edit**.
   - Paste this JSON:
     ```json
     [
       {
         "AllowedHeaders": ["*"],
         "AllowedMethods": ["GET", "PUT", "POST", "HEAD"],
         "AllowedOrigins": ["*"],
         "ExposeHeaders": []
       }
     ]
     ```
   - Click **Save changes**.

---

## Step 2: Create the AWS Lambda Function

1. Search for **Lambda** in the AWS console and open it.
2. Click **Create function**:
   - Select **Author from scratch**.
   - **Function name**: `agronex_relay_handler`
   - **Runtime**: `Python 3.11` (or `Python 3.12`)
   - **Architecture**: `x86_64`
   - Click **Create function**.

3. **Paste Lambda Code**:
   - Under the **Code** tab, open `lambda_function.py`.
   - Delete any default code.
   - Open [aws/lambda_function.py](file:///c:/Users/Nikhil/OneDrive/Desktop/Major%20project/aws/lambda_function.py) from this project, copy its entire contents, and paste it into the Lambda code editor.
   - Click **Deploy**.

4. **Set Environment Variable**:
   - Click the **Configuration** tab → **Environment variables** (on the left menu) → **Edit**.
   - Click **Add environment variable**:
     - **Key**: `S3_BUCKET`
     - **Value**: Your bucket name from Step 1 (e.g. `agronex-pi-data-nikhil`).
   - Click **Save**.

5. **Increase Timeout & Memory**:
   - Under the **Configuration** tab → **General configuration** → **Edit**:
     - **Timeout**: Change from `3 sec` to `30 sec`.
     - **Memory**: Change from `128 MB` to `256 MB`.
   - Click **Save**.

6. **Grant S3 Permissions to Lambda**:
   - Under the **Configuration** tab → **Permissions**.
   - Click on the **Role name** (opens IAM console in a new tab).
   - In the IAM tab, click **Add permissions** → **Attach policies**.
   - Search for `AmazonS3FullAccess`, select the checkbox, and click **Add permissions**.
   - Close the IAM tab.

---

## Step 3: Create the API Gateway (HTTP API)

1. Search for **API Gateway** in the AWS console and open it.
2. Look for **HTTP API** and click **Build**:
   - Click **Add integration**.
   - Choose **Lambda**.
   - **Lambda function**: Select `agronex_relay_handler`.
   - **API name**: `agronex-api`
   - Click **Next**.
3. **Configure routes**:
   - Under **Resource path**, select:
     - Method: `ANY`
     - Path: `/{proxy+}`
   - Click **Next**.
4. **Configure stages**:
   - Leave stage name as `$default` (with Auto-deploy enabled).
   - Click **Next**, then **Create**.

5. **Enable CORS in API Gateway**:
   - In the left menu of API Gateway, click **CORS** (under Develop).
   - Click **Configure**:
     - **Access-Control-Allow-Origin**: `*`
     - **Access-Control-Allow-Headers**: `*`
     - **Access-Control-Allow-Methods**: `GET`, `POST`, `OPTIONS`
   - Click **Save**.

6. **Copy Your Invoke URL**:
   - Go to **Stages** or the API overview.
   - Copy the **Invoke URL** (e.g. `https://abc123xyz.execute-api.ap-south-1.amazonaws.com`).

---

## Step 4: Connect the Raspberry Pi

On the Raspberry Pi, set your API URL in either of two ways:

### Option A: Environment Variable (Recommended)
Add this line to `~/.bashrc` on the Raspberry Pi:
```bash
export AGRONEX_AWS_URL="https://your-api-id.execute-api.ap-south-1.amazonaws.com"
```
Then reload:
```bash
source ~/.bashrc
```

### Option B: Directly in `config.py`
In [config.py](file:///c:/Users/Nikhil/OneDrive/Desktop/Major%20project/config.py), update line 164:
```python
AWS_API_URL = os.environ.get(
    "AGRONEX_AWS_URL",
    "https://your-api-id.execute-api.ap-south-1.amazonaws.com"
)
```

Now start the robot supervisor:
```bash
python main.py
```
You will see:
```
[INFO] AgroNex.AWSRelay: AWS Relay enabled → https://your-api-id...
[INFO] AgroNex.AWSRelay: AWS Relay thread started.
[INFO] AgroNex.Main: Auto-Scan Green Detection loop running.
```

---

## Step 5: Launch the Remote Cloud Dashboard

You can host the dashboard using **S3 Static Website Hosting** so you can view it from anywhere in the world on any mobile phone or laptop:

1. In the AWS S3 Console, open your bucket `agronex-pi-data-<your-name>`.
2. Go to the **Properties** tab → scroll to the bottom → **Static website hosting** → **Edit**.
   - Select **Enable**.
   - **Index document**: `index.html`.
   - Click **Save changes**.
3. Go to the **Objects** tab → click **Upload**.
   - Select [aws/agronex_dashboard/index.html](file:///c:/Users/Nikhil/OneDrive/Desktop/Major%20project/aws/agronex_dashboard/index.html).
   - Click **Upload**.
4. Open the **Bucket website endpoint URL** shown at the bottom of the Properties tab (e.g. `http://agronex-pi-data-nikhil.s3-website.ap-south-1.amazonaws.com`).
5. Click **⚙️ Configure** in the top bar of the dashboard, enter your API Gateway Invoke URL, and click **Save & Connect**.
6. That's it! Your mobile phone or laptop now receives live telemetry, GPS coordinates, real-time actuator toggles, and auto-captured leaf disease scans with zero manual photo uploads!
