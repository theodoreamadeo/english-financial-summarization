OUTPUT_REGULATION_SECTION_1 = """
Section 1: Company Overview

1.1 Basic Information
    Format: Field | Value

    1.1.1 Company Name
        Instruction: Extract the official legal name exactly as printed (retain suffixes like Inc., Ltd., plc; remove ™/®). 

    1.1.2 Establishment Date
        Instruction: Extract the date when the company was officialy founded, created, or incorporated. Preserve the report's date format in Month Day, Year (e.g., January 1, 2000), Month, Year (e.g., January 2000) or Year only (e.g., 2000).

    1.1.3 Headquarters Location (City and Country)
        Instruction: Extract the city and country of the company's headquarters as written in the report. If the country is not explicitly mentioned, infer it from the city or other context in the report.

1.2 Core Competencies
    Format: Perspective | {Year} Report
    Missing: Return "N/A".

    1.2.1 Innovation Advantages
        Instruction: Summarize the company's innovation strengths. Provide specific, report-backed examples (e.g., patents, R&D intensity, proprietary tech). Focus on how the innovations contribute to competitive advantage. Include any numerical data and citations where available.

    1.2.2 Product Advantages
        Instruction: Summarize the company's product strengths. Highlight unique features, quality, customer satisfaction, and market differentiation. Provide explanation about how these product is better than competitors.
        
    1.2.3 Brand Recognition
        Instruction: Explain the brand's market presence and how the society recognizes the brand. Avoid marketing slogans unless explicitly framed as recognition. May include on how the brand maintains their recognition/existence if available.

    1.2.4 Reputation Ratings
        Instruction: Explain the company's reputation in the market. Include awards, rankings, patents, certifications, and recognitions with citations inside the report. May include how the company maintains its reputation if available.

1.3 Mission & Vision
    Format: Field | Value
    
    1.3.1 Mission Statement
    1.3.2 Vision Statement
    1.3.3 Core Values
"""

OUTPUT_REGULATION_SECTION_2 = """
Section 2: Financial Performance
Instruction: Follow strictyly the subsection order, do not skip or invent any new subsection. Extract the financial numerical data inside the report for all years. If any calculation involved, the result must be written in 2 decimal places. Lastly, separate thousands with commas.
Missing: Return "N/A".

2.1 Income Statement
    Format: Field | {Year} | Multiplier | Currency

    2.1.1. Revenue
    2.1.2. Cost of Goods Sold (COGS)
    2.1.3. Gross Profit
    2.1.4. Operating Expenses
    2.1.5. Operating Income
    2.1.6. Net Income
    2.1.7. Income before income taxes
    2.1.8. Income tax expense (benefit)

2.2 Balance Sheet
    Format: Field | {Year} | Multiplier | Currency

    2.2.1. Total Assets
    2.2.2. Current Assets
    2.2.3. Non-Current Assets 
    2.2.4. Total Liabilities
    2.2.5. Current Liabilities
    2.2.6. Non-Current Liabilities
    2.2.7. Shareholders' Equity
    2.2.8. Retained Earnings
    2.2.9. Total Equity and Liabilities
    2.2.10. Inventories
    2.2.11. Prepaid Expenses

2.3 Cash Flow Statement
    Format: Field | {Year} | Multiplier | Currency

    2.3.1. Net Cash Flow from Operations
    2.3.2. Net Cash Flow from Investing
    2.3.3. Net Cash Flow from Financing
    2.3.4. Net Increase/Decrease in Cash
    2.3.5. Dividends 

2.4 Key Financial Metrics
    Instruction: All the result must be written in percentage (%) and 2 decimal places. If one of the inputs needed for a calculation is missing, set the result to `N/A`.

    Format: Field | {Year}

    2.4.1. Gross Margin = (Revenue - COGS) ÷ Revenue
    2.4.2. Operating Margin = Operating Income ÷ Revenue
    2.4.3. Net Profit Margin = Net Income ÷ Revenue
    2.4.4. Current Ratio = Current Assets ÷ Current Liabilities
    2.4.5. Quick Ratio = (Current Assets - Inventories - Prepaid expenses) ÷ Current Liabilities
    2.4.6. Interest Coverage = Operating Income ÷ Interest Expense 
    2.4.7. Asset Turnover = Revenue ÷ Average Total Assets
    2.4.8. Debt-to-Equity = Total Debt ÷ Shareholders' Equity
    2.4.9. Return on Equity (RoE) = Net Income ÷ Average Shareholders' Equity
    2.4.10. Return on Assets (RoA) = Net Income ÷ Average Total Assets
    2.4.11. Effective Tax Rate = Income tax expense (benefit) ÷ Income before income taxes
    2.4.12. Dividend Payout Ratio = Dividends ÷ Net Income

2.5 Operating Performance
    Format: Field | {Year}

    2.5.1. Revenue by Product/Service: What is the revenue breakdown by product/service?
        Instruction: Break down the total revenue by each major product or service line as reported. Provide the revenue figures for each product/service in the same currency and multiplier as the total revenue. At the end, include a total to ensure it matches the overall revenue figure (e.g., Total: $60,922M). Categorize products/services based on their function or market segment as per the report.

    2.5.2. Revenue by Geographic Region: What is the revenue breakdown by geographic region?
        Instruction: Break down the total revenue by each major geographic region as reported. Provide the revenue figures for each region in the same currency and multiplier as the total revenue. At the end, include a total to ensure it matches the overall revenue figure (e.g., Total: $60,922M). Categorize regions based on standard geographic divisions (e.g., North America, Europe, Asia-Pacific) as per the report.
"""

OUTPUT_REGULATION_SECTION_3 = """
Section 3: Business Analysis
Instruction: Determine the company's business performance from years to years, focusing on analyzing the trend and reasons behind the changes. Includes quantitative data and qualitative insights. Any quantitative data must be written in 2 decimal places. Separate thousands with commas. Write all the subsection outputs in markdown table format, no bulleted lists or free-form paragraphs.
Missing: Return "N/A".

3.1 Profitability Analysis
    Format: Perspective | Answer

    3.1.1. Revenue & Direct-Cost Dynamics
        Instruction: Explain the trend of company's revenue grow rates, gross margins, and revenue distribution by product/service and geographic region over the reported periods. Include the quantitative data to support your analysis and written it in 2 decimal places.

    3.1.2. Operating Efficiency
        Instruction: Evaluate the company's operating efficiency by examining operating expenses, operating income, and operating margins. Identify trends in cost management and operational performance over the reported periods. Write all the quantitative data in 2 decimal places.

    3.1.3. External & One-Off Impact
        Instruction: Explain the trend of effective tax rate over the reported periods. Other than that, assess the non-recurring items that have affected profitability. Include quantitative data to support your analysis and written it in 2 decimal places.

3.2 Financial Performance Summary
    Instruction: Analyze the company's overall financial performance from years to years, focusing on key areas that may become the key matrics to determine the company's financial performance. Determine the trends and provide the value written in 2 decimal places. Analyze the growth or trends observed in the income statement, balance sheet, and cash flow statement, key financial metrics, and operating performance. Include key financial ratios, trends, and comparisons to the previous periods. Write all the quantitative data in 2 decimal places.

    Format: Perspective | {Year} Report

    3.2.1. Comprehensive financial health
    3.2.2. Profitability and earnings quality
    3.2.3. Operational efficiency
    3.2.4. Financial risk identification and early warning
    3.2.5. Future financial performance projection

3.3 Business Competitiveness
    Format: Field | {Year} Report

    3.3.1. Business Model: What is the company's primary business model (e.g., subscription, freemium, sales)?
        Instruction: Describe the company's primary business model. Include how the company generates revenue, its target customer segments, and any unique aspects of its business model that differentiate it from competitors.

    3.3.2. Market Position: What is the company's market share in each of its key markets? Is the company a leader, challenger, or niche player?
        Instruction: Analyze the company's market position in its key markets. Provide estimates of market share where available, and classify the company as a market leader, challenger, or niche player based on its competitive standing.   
"""


OUTPUT_REGULATION_SECTION_4 = """
Section 4: Risk Factors
Format: Perspective | {Year} Report
Missing: Return "N/A".

4.1 Risk Factors
    4.1.1. Market Risks
        Instruction: Identify and assess the key market risks that may impact the company's performance, starting from competition, market demand, economic conditions, political factors, and etc. Provide insights into how these risks are damaging the company's prospects.

    4.1.2. Operational Risks
        Instruction: Identify and evaluate the operational risks faced by the company, including supply chain disruptions, technology failures, and human resource challenges. Discuss the impact of these risks on the company's operations and financial performance.

    4.1.3. Financial Risks
        Instruction: Analyze the financial condition that may impact the company's performance. Explain how these risks are damaging the company's prospects.

    4.1.4. Compliance Risks
        Instruction: Examine the compliance risks related to regulatory changes, legal issues, and industry standards. Discuss how the compliance risks may affect the company's operations and reputation.
"""

OUTPUT_REGULATION_SECTION_5 = """
Section 5: Corporate Governance

5.1 Board Composition
    Format: Name | Position | Total Income
    Missing: Return "N/A".

    5.1.1. Name
        Instruction: List all board members as per the annual report, including both executive and non-executive directors. Ensure names are spelled exactly as in the report.

    5.1.2. Position
        Instruction: Specify the position of each board member (e.g., Chairman, CEO, CFO, Independent Director) as stated in the report.

    5.1.3. Total Income
        Instruction: Extract the total income (including salary, bonuses, stock options, and other compensation) for each board member as reported in the annual report.

5.2 Internal Controls
    Format: Field | {Year} Report
    Missing: Return "N/A".

    5.2.1. Risk assessment procedures
        Instruction: Explain the company's procedure for assessing risks as part of their internal control system.

    5.2.2. Control activities
        Instruction: Explain the activities the company implements to maintain control over their operations.
        
    5.2.3. Monitoring mechanisms
        Instruction: Explain the mechanisms on how the company monitors their daily operations.

    5.2.4. Identified material weaknesses or deficiencies
        Instruction: Summarize on how the company determine their material weaknesses or deficiencies

    5.2.5. Improvements
        Instruction: Summarize on how the company improves their internal control system. 

    5.2.6. Effectiveness
        Instruction: Summarize on how the company evaluates the effectiveness of their internal control system. 
"""

OUTPUT_REGULATION_SECTION_6 = """
Section 6: Future Outlook
Format: Field | {Year} Report
Missing: Return "N/A".

6.1 Strategic Direction
    6.1.1. Mergers and acquisitions (M&A) to expand market share
        Instruction: Summarize the company's merger and acquisition strategy. Include any specific targets or sectors mentioned for potential acquisitions.

    6.1.2. Acquire new technologies
        Instruction: Summarize the company's strategy for implementing new technologies into their final products. Include any specific technologies or innovation areas mentioned in the report.

    6.1.3. Potential for organizational restructuring
        Instruction: Summarize any plans for organizational restructuring mentioned in the report. Include the reasons for restructuring and expected outcomes.

6.2 Challenges and Uncertainties
    6.2.1. Economic challenges such as inflation, recession risks, and shifting consumer behavior that could impact revenue and profitability.
    6.2.2. Competitive pressures from both established industry players and new, disruptive market entrants that the company faces

6.3 Innovation and Development Plans
    6.3.1. R&D investments, with a focus on advancing technology, improving products, and creating new solutions to cater to market trends
    6.3.2. New product launches, emphasizing the company's commitment to continuously introducing differentiated products
"""

OUTPUT_REGULATION = [
    OUTPUT_REGULATION_SECTION_1,
    OUTPUT_REGULATION_SECTION_2,
    OUTPUT_REGULATION_SECTION_3,
    OUTPUT_REGULATION_SECTION_4,
    OUTPUT_REGULATION_SECTION_5,
    OUTPUT_REGULATION_SECTION_6
]