OUTPUT_STRUCTURE_SECTION_1 = """
Section 1: Company Overview

1.1 Basic Information
    1.1.1 Company Name
    1.1.2. Establishment Date
    1.1.3. Headquarters Location (City and Country)

1.2 Core Competencies
    1.2.1. Innovation Advantages
    1.2.2. Product Advantages
    1.2.3. Brand Recognition
    1.2.4. Reputation Ratings

1.3 Mission & Vision
    1.3.1. Mission Statement
    1.32. Vision Statement
    1.3.3. Core Value
"""

OUTPUT_STRUCTURE_SECTION_2 = """
Section 2: Financial Performance

2.1 Income Statement
    2.1.1. Revenue
    2.1.2. Cost of Goods Sold (COGS)
    2.1.3. Gross Profit
    2.1.4. Operating Expenses
    2.1.5. Operating Income
    2.1.6. Net Income
    2.1.7. Income before income taxes
    2.1.8. Income tax expense (benefit)

2.2 Balance Sheet
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
    2.3.1. Net Cash Flow from Operations
    2.3.2. Net Cash Flow from Investing
    2.3.3. Net Cash Flow from Financing
    2.3.4. Net Increase/Decrease in Cash
    2.3.5. Dividends 

2.4 Key Financial Metrics
    2.4.1. Gross Margin = (Revenue - COGS) ÷ Revenue
    2.4.2. Operating Margin = Operating Income ÷ Revenue
    2.4.3. Net Profit Margin = Net Income ÷ Revenue
    2.4.4. Current Ratio = Current Assets ÷ Current Liabilities
    2.4.5. Quick Ratio = (Current Assets − Inventories − Prepaid expenses) ÷ Current Liabilities
    2.4.6. Interest Coverage = Operating Income ÷ Interest Expense 
    2.4.7. Asset Turnover = Revenue ÷ Average Total Assets
    2.4.8. Debt-to-Equity = Total Debt ÷ Shareholders’ Equity
    2.4.9. Return on Equity (RoE) = Net Income ÷ Average Shareholders’ Equity
    2.4.10. Return on Assets (RoA) = Net Income ÷ Average Total Assets
    2.4.11. Effective Tax Rate = Income tax expense (benefit) ÷ Income before income taxes
    2.4.12. Dividend Payout Ratio = Dividends ÷ Net Income

2.5 Operating Performance
    2.5.1. Revenue by Product/Service: What is the revenue breakdown by product/service?
    2.5.2. Revenue by Geographic Region: What is the revenue breakdown by geographic region?
"""

OUTPUT_STRUCTURE_SECTION_3 = """
Section 3: Business Analysis

3.1 Profitability Analysis
    3.1.1. Revenue & Direct-Cost Dynamics
    key metrics: Revenue Growth ; Gross Margin; Revenue by Product/Service; Revenue by Geographic Region
    3.1.2. Operating Efficiency
    key metrics: Operating Margin
    3.1.3. External & One-Off Impact
    key metrics: Effective Tax Rate, Non-Recurring Items

3.2 Financial Performance Summary
    3.2.1. Comprehensive financial health
    3.2.2. Profitabilitiy and earnings quality
    3.2.3. Operational efficiency
    3.2.4. Financial risk identification and early warning
    3.2.5. Future financial performance projection

3.3 Business Competitiveness
    3.3.1. Business Model: What is the company's primary business model (e.g., subscription, freemium, sales)?
    3.3.2. Market Position: What is the company's market share in each of its key markets? Is the company a leader, challenger, or niche player?
"""


OUTPUT_STRUCTURE_SECTION_4 = """
Section 4: Risk Factors

4.1 Risk Factors
    4.1.1. Market Risks
    4.1.2. Operational Risks
    4.1.3. Financial Risks
    4.1.4. Compliance Risks
"""

OUTPUT_STRUCTURE_SECTION_5 = """
Section 5: Corporate Governance

5.1 Board Composition
    5.1.1. Name
    5.1.2. Position
    5.1.3. Total Income

5.2 Internal Controls
    5.2.1. Risk assessment procedures
    5.2.2. Control activities
    5.2.3. Monitoring mechanisms
    5.2.4. Identified material weaknesses or deficiencies
    5.2.5. Improvements
    5.2.6. Effectiveness
"""

OUTPUT_STRUCTURE_SECTION_6 = """
Section 6: Future Outlook

6.1 Strategic Direction
    6.1.1. Mergers and acquisitions (M&A) to expand market share
    6.1.2. Acquire new technologies
    6.1.3. Potential for organizational restructuring

6.2 Challenges and Uncertainties
    6.2.1. Economic challenges such as inflation, recession risks, and shifting consumer behavior that could impact revenue and profitability.
    6.2.2. Competitive pressures from both established industry players and new, disruptive market entrants that the company faces

6.3 Innovation and Development Plans
    6.3.1. R&D investments, with a focus on advancing technology, improving products, and creating new solutions to cater to market trends
    6.3.2. New product launches, emphasizing the company’s commitment to continuously introducing differentiated products
"""

OUTPUT_STRUCTURE = [
    OUTPUT_STRUCTURE_SECTION_1,
    OUTPUT_STRUCTURE_SECTION_2,
    OUTPUT_STRUCTURE_SECTION_3,
    OUTPUT_STRUCTURE_SECTION_4,
    OUTPUT_STRUCTURE_SECTION_5,
    OUTPUT_STRUCTURE_SECTION_6
]