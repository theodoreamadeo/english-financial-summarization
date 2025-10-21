from openai import OpenAI
from dotenv import load_dotenv
from output_sample import OUTPUT_SAMPLE
from output_structure import OUTPUT_STRUCTURE
from output_regulation import OUTPUT_REGULATION


import tiktoken
import os
import requests
import time
import zipfile
import io

# Load environment variables from .env file
load_dotenv()
MINERU_API_KEY = os.getenv("MINERU_API_KEY")
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")

REPORT_MD_PATH = "report_md"
OUTPUT_PATH = "output"

if not os.path.isdir(REPORT_MD_PATH):
    os.mkdir(REPORT_MD_PATH)
if not os.path.isdir(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)

# PDF to Markdown conversion for multiple files
def pdf_to_markdown(files):
    for file in files:
        file_name = file[0][:-4]
        file_path = f"{REPORT_MD_PATH}/{file_name}.md"
        if os.path.exists(file_path):
            print(f"{file_name}.md already exists, skipping conversion.")
            continue
        else:
            task_id = create_pdf_task(file, MINERU_API_KEY)
            zip_url = get_task_result(task_id, MINERU_API_KEY, file)
            markdown_text = download_and_extract_md(zip_url)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(markdown_text)
            print(f"Saved markdown for {file_name}.md")

# Create a batch task for multiple PDF files
def create_pdf_batch(files_input, token):
    url = "https://mineru.net/api/v4/extract/task/batch"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    files = []
    for file in files_input:
        file_name = file[0]
        file_url = file[1]
        files.append({"url": file_url, "is_ocr": True, "data_id": file_name})

    data = {
        "enable_formula": True,
        "enable_table": True,
        "files": files
    }
    try:
        response = requests.post(url,headers=header,json=data)
        if response.status_code == 200:
            result = response.json()
            print('response success. result:{}'.format(result))
            if result["code"] == 0:
                batch_id = result["data"]["batch_id"]
                print('Batch_id:{}'.format(batch_id))
                return batch_id
            else:
                print('Submit task failed,reason:{}'.format(result.msg))
        else:
            print('Response not success. status:{} ,result:{}'.format(response.status_code, response))
    except Exception as err:
        print(err)

# Poll for batch task result
def get_batch_result(batch_id, token):
    url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    full_zip_urls = []
    file_failed = []
    file_running_count = 0
    if response.status_code == 200:
        data = response.json()
        extract_result = data["data"]["extract_result"]
        # print(extract_result)
        for result in extract_result:
            if result["state"] == "done":
                full_zip_urls.append((result["data_id"],result["full_zip_url"]))
            elif result["state"] == "failed":
                file_failed.append(result["data_id"])
            else:
                file_running_count += 1
        return full_zip_urls, file_failed, file_running_count
    else:
        print(f"Request failed, error code: {response.status_code}")

# Download ZIP file and extract Markdown content for batch
def download_and_extract_md_batch(files):
    for file in files:
        zip_url = file[1]
        file_name = file[0][:-4]

        file_path = f"{REPORT_MD_PATH}/{file_name}.md"
        markdown_text = download_and_extract_md(zip_url)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_text)
            print(f"Saved markdown for {file_name}.md")
        
# Create a task for a PDF file
def create_pdf_task(file, token):
    url = "https://mineru.net/api/v4/extract/task"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    file_name = file[0]
    file_url = file[1]
    
    data = {
        "url": file_url,
        "language": "en", # en stands for English
        "is_ocr": True,            
        "enable_formula": True,    
        "enable_table": True,
        "data_id": file_name,
        "model_version": "vlm" # use "vlm" for better layout recognition
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        print(f"Create task response: {response_data}")
        
        # Check if the response contains the expected data structure
        if "data" in response_data and "task_id" in response_data["data"]:
            task_id = response_data["data"]["task_id"]
            print(f"Created task for {file_url}, task_id = {task_id}")
            return task_id
        else:
            # Handle API error response
            error_msg = response_data.get("msg", "Unknown error")
            error_code = response_data.get("code", "Unknown code")
            raise Exception(f"API Error - Code: {error_code}, Message: {error_msg}")
    else:
        raise Exception(f"Create task failed - Status: {response.status_code}, Response: {response.text}")


# Poll for task result
def get_task_result(task_id, token, file, max_retries=30, retry_interval=30):
    url = f"https://mineru.net/api/v4/extract/task/{task_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                
                # Check if response has expected structure
                if "data" not in data:
                    print(f"Unexpected API response structure: {data}")
                    time.sleep(retry_interval)
                    continue
                    
                status = data["data"]["state"]            
                if status == "done":
                    # Return zip file url
                    return data["data"]["full_zip_url"]
                elif status == "failed":
                    error_msg = data["data"].get("err_msg", "Unknown error")
                    print(f"Processing failed: {error_msg}. Creating a new task to retry.")
                    # Create a new task to retry
                    try:
                        new_task_id = create_pdf_task(file, token)
                        print(f"New task created with ID: {new_task_id}")
                        return get_task_result(new_task_id, token, file, max_retries, retry_interval)
                    except Exception as e:
                        print(f"Failed to create retry task: {e}")
                        raise Exception(f"Task failed and retry creation failed: {e}")
                elif status == "running":
                    progress = data["data"].get("extract_progress", "Unknown")
                    print(f"Current status: {status}, progress: {progress}")
                else:
                    print(f"Current status: {status}, waiting {retry_interval} seconds before checking again.")
            else:
                print(f"Request failed with status code: {response.status_code}, response: {response.text}")
                
        except Exception as e:
            print(f"Error during attempt {attempt + 1}: {e}")
            
        time.sleep(retry_interval)  # Wait before retry
    
    raise Exception("Time out while waiting for task completion")

# Download ZIP file and extract Markdown content
def download_and_extract_md(zip_url):
    response = requests.get(zip_url)
    zip_bytes = io.BytesIO(response.content)

    with zipfile.ZipFile(zip_bytes) as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith(".md"):
                with zip_ref.open(file_name) as md_file:
                    return md_file.read().decode("utf-8")

    raise Exception("Cannot find Markdown file in the ZIP")

def get_report_text(fils):
    report_text = ""
    for file in fils:
        year = file[0][-8:-4]
        file_name = file[0][:-4]
        file_path = f"report_md/{file_name}.md"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                markdown_text = file.read()
            report_text += f"[{year} Annual Report START]\n\n" + markdown_text + f"\n\n[{year} Annual Report END]\n\n\n"
        else:
            print(f"{file_name}.md does not exist, please run pdf_to_markdown function first.")
            return None
    return report_text

def count_tokens(text, model_name = "gemini-2.5-flash"):
    """Count tokens for debugging purposes."""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def log_token_usage(component_name, text, model_name = "gemini-2.5-flash"):
    """Log token usage with simple formatting."""
    token_count = count_tokens(text, model_name)
    print(f"\n[TOKEN DEBUG] {component_name}: {token_count:,} tokens ({len(text):,} chars)")
    return token_count

personna_text = """
    As a financial analyst in a leading investment firm, you are tasked to intepret and analyze the annual reports of companies. You have extensive experience in financial statement analysis, ratio analysis, and business performance evaluation. Your goal is to provide clear, concise, and insightful reports that help stakeholders make informed decisions. You must be careful when doing any calculations, so that the stakeholders may not take any wrong actions based on your report. You should strictly follow the output structure provided, ensuring that all sections and subsections are addressed in detail. Your analysis should be data-driven, leveraging the financial data presented in the reports to support your conclusions. Always maintain a professional tone and ensure accuracy in your reporting. 
"""

class Model:
    def __init__(self, name, model):
        self.name = name
        self.model = model
        self.client = OpenAI(
            api_key=OPEN_ROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

    # upload local file to get file_id
    def upload_file(self,path: str):
        with open(path, "rb") as f:
            file_obj = self.client.files.create(file=f, purpose="user_data")
        print(f"Uploaded {path}, file_id = {file_obj.id}")
        return file_obj.id

    def report (self, prompt):
        model = self.name+"/"+self.model
        response = self.client.chat.completions.create(
                model=model,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": personna_text},
                    {"role": "user", "content": prompt}
                ]
            )  
        return response.choices[0].message.content

if __name__ == "__main__":
    # ----------------------- ONE COMPANY PROCESS PIPELINE START -----------------------
    model = Model("google", "gemini-2.5-flash")

    # Insert PDF files here as (file_name, file_url)
    files_input = [
        # ("Spirent_Communications_PLC_2024.pdf","https://assets.ctfassets.net/63dbmymdqn3g/6oL1xJK6z4ui2ebRZ3HLFa/b04bac41390a90f4f6a87a69e001ca1f/SPR_AR24_Full_file_for_website_colour_updated.pdf"),
        # ("Spirent_Communications_PLC_2023.pdf","https://assets.ctfassets.net/63dbmymdqn3g/28kH3rewrykewiybTRF4TX/3e3d054fff433da3b537c6f58cb50e18/Spirent_Communications_plc_Annual_Report_2023.pdf"),
        # ("Gamma_Communications_PLC_2024.pdf","https://gammagroup.co/wp-content/uploads/2025/04/Gamma-Annual-Report-2024.pdf"),
        # ("Gamma_Communications_PLC_2023.pdf","https://gammagroup.co/wp-content/uploads/2024/03/Gamma-Annual-Report-and-Accounts-2023.pdf"),
        # ("Rolls-Royce_Holdings_PLC_2024.pdf","https://www.rolls-royce.com/~/media/Files/R/Rolls-Royce/documents/annual-report/2025/2024-annual-report.pdf"),
        # ("Rolls-Royce_Holdings_PLC_2023.pdf","https://www.rolls-royce.com/~/media/Files/R/Rolls-Royce/documents/annual-report/2024/2023-annual-report.pdf"),
        # ("Babcock_International_Group_PLC_2024.pdf","https://www.babcockinternational.com/wp-content/uploads/2025/06/Babcock-Annual-Report-Financial-Statements-2024.pdf"),
        # ("Babcock_International_Group_PLC_2023.pdf","https://www.babcockinternational.com/wp-content/uploads/2025/06/Annual-Report-and-Financial-Statements-2023.pdf"),
        # ("QinetiQ_Group_PLC_2024.pdf","https://www.qinetiq.com/-/media/d07f6674600b4c7eb27db3e46c30bc60.ashx"),
        # ("QinetiQ_Group_PLC_2023.pdf","https://www.qinetiq.com/-/media/8f8ed30f273744e3b5362c275bcf2b39.ashx"),
        # ("Select_Harvests_2024.pdf","https://selectharvests.com.au/documents/SHV_Annual_Report_2024_19_Dec_2024_ASX.pdf"),
        # ("Select_Harvests_2023.pdf","https://selectharvests.com.au/documents/Select_Harvests_Annual_Report_2023B.pdf"),
        # ("NEXTDC_Limited_2024.pdf","https://www.nextdc.com/hubfs/Financial%20Reports/280827%20-%20FY24%20NEXTDC%20Annual%20Report.pdf"),
        # ("NEXTDC_Limited_2023.pdf","https://www.nextdc.com/hubfs/ASX%20Announcements/2597206-%20NXT%20-%20FY23%20Annual%20Report.pdf"),
        # ("Spark_New_Zealand_Limited_2024.pdf","https://www.spark.co.nz/content/dam/spark/documents/pdfs/governance/Annual_Report_(2024)_.pdf?srsltid=AfmBOopSBVp_t3G3g5dOz9EpE4M5Cwz7DLw6DQ6br4hJ_oBzEgnOWEwf"),
        # ("Spark_New_Zealand_Limited_2023.pdf","https://www.sparknz.co.nz/content/dam/SparkNZ/pdf-documents/governance/Annual_Report_(2023).pdf"),
        # ("Ai-Media_Technologies_Limited_2024.pdf","https://webservices.weblink.com.au/article.aspx?articleID=QvYGElLyl2WTKG/SCKSy/Q=="),
        # ("Ai-Media_Technologies_Limited_2023.pdf","https://webservices.weblink.com.au/article.aspx?articleID=69hqXu0ndrwd5STyw+HfBw=="),
        # ("Metcash_Limited_2024.pdf","https://www.metcash.com/wp-content/uploads/2024/08/21068_Metcash_AR24_Web_V1.pdf"),
        # ("Metcash_Limited_2023.pdf","https://www.metcash.com/wp-content/uploads/2023/08/20837_Metcash_AR23_00_FULL_Web_V1.pdf"),
        # ("Compass_Minerals_International_2024.pdf","https://d18rn0p25nwr6d.cloudfront.net/CIK-0001227654/adac569d-a12f-4a8a-8089-1c734d41d5d1.pdf"),
        # ("Compass_Minerals_International_2023.pdf","https://d18rn0p25nwr6d.cloudfront.net/CIK-0001227654/3694176b-86b1-4cff-8d9f-4c66d9dca284.pdf"),
        # ("UnitedHealth_Group_Incorporated_2024.pdf","https://www.unitedhealthgroup.com/content/dam/UHG/PDF/investors/2024/UNH-Q4-2024-Form-10-K.pdf"),
        # ("UnitedHealth_Group_Incorporated_2023.pdf","https://www.unitedhealthgroup.com/content/dam/UHG/PDF/investors/2023/UNH-Q4-2023-Form-10-K.pdf"),
        # ("Centene_Corporation_2024.pdf","https://app.quotemedia.com/data/downloadFiling?webmasterId=101533&ref=318929194&type=PDF&symbol=CNC&cdn=9f07d22ab04aec392332c75556349640&companyName=Centene+Corporation&formType=10-K&dateFiled=2025-02-18"),
        # ("Centene_Corporation_2023.pdf","https://app.quotemedia.com/data/downloadFiling?webmasterId=101533&ref=318084359&type=PDF&symbol=CNC&cdn=780a95abe43da50efe459df23e158299&companyName=Centene+Corporation&formType=10-K&dateFiled=2024-02-20"),
        # ("The_Home_Depot_Inc_2024.pdf","https://otp.tools.investis.com/clients/us/home_depot/SEC/sec-show.aspx?FilingId=18302429&Cik=0000354950&Type=PDF&hasPdf=1"),
        # ("The_Home_Depot_Inc_2023.pdf","https://otp.tools.investis.com/clients/us/home_depot/SEC/sec-show.aspx?FilingId=17366192&Cik=0000354950&Type=PDF&hasPdf=1"),
        # ("DICK'S_Sporting_Goods_Inc_2024.pdf","https://d18rn0p25nwr6d.cloudfront.net/CIK-0001089063/76c9cf7e-cef3-4b7f-b468-810d3ba16411.pdf"),
        # ("DICK'S_Sporting_Goods_Inc_2023.pdf","https://d18rn0p25nwr6d.cloudfront.net/CIK-0001089063/aeb0cde9-90f9-4640-81d4-301a9fe1c857.pdf"),
        ("CBL_&_Associates_Properties_Inc_2024.pdf","https://d18rn0p25nwr6d.cloudfront.net/CIK-0000910612/63fb379b-8ca4-460d-9199-3cca36531dc1.pdf"),
        ("CBL_&_Associates_Properties_Inc_2023.pdf","https://d18rn0p25nwr6d.cloudfront.net/CIK-0000910612/24b388ec-ba69-4ee6-8279-4fa0680430f6.pdf"),

    ]
    pdf_to_markdown(files_input)

    pdf_text = get_report_text(files_input)

    log_token_usage("Combined PDF Text", pdf_text)

    final_report = ""
    for i in range(len(OUTPUT_STRUCTURE)):
        print(f"============ Processing Section {i+1} ============\n")
        prompt = f"""
            Generate an in-depth comparative report for the company based on year 2023 and 2024 annual reports.  

            **Data Input Specifications:**  
            1. Report content is located within marked intervals:  
            - Report 2024: `[2024 Annual Report START]` to `[2024 Annual Report END]`  
            - Report 2023: `[2023 Annual Report START]` to `[2023 Annual Report END]`  
            2. Raw text is provided in converted format:

            {pdf_text}

            **Output Structure Requirements (Mandatory Compliance):**
            1. Strictly follow the section and subsection order. The output structure must mirror the given format precisely, with no missing sections, no reordering, and no deviation from the specified structure or style. Output structure is as follows:
            
            {OUTPUT_STRUCTURE[i]}

            2. Follow the specific instructions and questions listed under each subsection. The analysis must be comprehensive and address all points raised. Instructions are as follows:

            {OUTPUT_REGULATION[i]}   

            3. Conduct in-depth analysis of the report of the company for the fiscal years 2023 and 2024.
            4. Each section and subsection must be clearly labeled as per the structure above.
            5. Ensure all key points listed under each subsection are addressed.
            6. Maintain a professional and analytical tone throughout the report.
            7. All the subsection outputs must be in markdown table format, no bulleted lists or free-form paragraphs
            8. The report should be concise yet comprehensive, focusing on critical insights and comparisons between the two fiscal years.
            
            **Output Example (Mandatory Compliance):**  
            Here is an example of the expected output format for Section {i+1} (format only; never reuse its content):

            {OUTPUT_SAMPLE[i]}

            **Important Notes:**  
            1. The output sample is provided only to illustrate the expected structure and formatting. Do not copy or use any content from the sample.
            2. Ensure that all numerical data is accurate and corresponds to the information provided in the annual reports.
            3. If any required data is missing from the reports, indicate "N/A".
            """

        # DEBUG: Log token usage for this section
        prompt_tokens = log_token_usage(f"Section {i+1} Prompt", prompt)
        
        # Check the token usage
        print(f"Tokens: {prompt_tokens:} ")

        try:
            response = model.report(prompt)
            print(response)

            if model.name == "google":
                # Gemini returns content directly, no </think> tags
                extracted_content = response.strip()
            else:
                # OpenAI models (o1-preview, etc.) may use </think> tags
                if "</think>" in response:
                    data = response.split("</think>", 1)
                    extracted_content = data[1].strip()
                else:
                    # Fallback: use full response if no delimiter found
                    extracted_content = response.strip()
            
            final_report += extracted_content + "\n\n"
            print(f"[SUCCESS] Section {i+1} completed\n")

            if i < len(OUTPUT_STRUCTURE) - 1:  # Don't delay after last section
                delay_seconds = 65  # Wait 65 seconds between sections
                print(f"[INFO] Waiting {delay_seconds}s before next section...")
                time.sleep(delay_seconds)

        except Exception as e:
            print(f"[ERROR] Section {i+1} failed: {e}\n")
            continue

    save_file_path = files_input[0][0][:-9] + "_report.md"
    with open(f"{OUTPUT_PATH}/{save_file_path}", 'w', encoding='utf-8') as file:
        file.write(final_report)
    print(f"Report {save_file_path} saved to output folder")