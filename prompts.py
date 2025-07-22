"""
Shared prompt definitions for investigation analysis.
This module contains prompts that can be used by both Perplexity and Gemini processors.
Prompts are tailored for an expert audience with high financial and market literacy.
"""

def get_base_investigation_info(investigation: dict) -> str:
    """Get the base investigation information for prompts."""
    return f"Investigation: {investigation['title']}\nDescription: {investigation['description']}"

def get_market_assessment_prompt(investigation: dict) -> str:
    """Get the market assessment prompt, refined for expert-level analysis."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Provide a rigorous, data-driven CURRENT MARKET ASSESSMENT suitable for an expert audience (assume the reader is a senior financial analyst, investor, or policymaker). Your analysis should include:
    - Total addressable market size in USD (global and US), with breakdowns by segment and recent CAGR. Reference authoritative sources and provide explicit assumptions.
    - Detailed analysis of current US import/export flows in this sector, including key HS codes, top trading partners, and recent trends. Quantify exposure to tariff risk.
    - Estimate the precise portion of the US market (by value and volume) that would be subject to tariffs if enacted, including downstream and indirect supply chain effects. Discuss substitution elasticity and potential for circumvention.
    - Identify and rank key market participants by market share, using the latest available data. Include both public and private firms, and discuss market concentration (e.g., HHI).
    - Analyze current trade patterns, major exporting/importing countries, and structural dependencies or vulnerabilities.
    
    Use advanced financial and market analysis frameworks where appropriate (e.g., Porter’s Five Forces, value chain analysis). Clearly state all assumptions, cite data sources, and highlight areas of uncertainty or debate. Provide actionable insights and implications for sophisticated stakeholders.
    """

def get_tariff_impact_prompt(investigation: dict) -> str:
    """Get the tariff impact analysis prompt, refined for expert-level analysis."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Provide a granular, scenario-based TARIFF IMPACT ANALYSIS for each tariff rate (10%, 25%, 50%), suitable for a financially sophisticated audience:
    - Quantify the estimated incremental cost to the US market under each scenario, assuming static trade patterns. Use sensitivity analysis to model key variables.
    - Critically assess the capacity and constraints of US companies to substitute for imports, including capital intensity, lead times, and regulatory barriers.
    - Model the expected shift in consumption to domestic markets, considering price elasticity of demand and supply, and potential for demand destruction or substitution.
    - Analyze the impact on supply chain structure, production costs, and gross margins for key industry segments.
    - Estimate the pass-through of tariff costs to end consumers, using historical analogs and economic theory.
    - Assess the aggregate demand impact in the US market, referencing macroeconomic multipliers and sectoral linkages.
    
    Support your analysis with quantitative models, explicit assumptions, and references to relevant academic or industry research. Highlight second-order effects, strategic responses by market participants, and discuss data limitations and uncertainties.
    """

def get_company_impact_prompt(investigation: dict) -> str:
    """Get the company impact analysis prompt, refined for expert-level analysis."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Provide a detailed, investor-grade COMPANY IMPACT ANALYSIS:
    - Identify and rank major companies (US and foreign) by exposure to the investigation, using quantitative metrics (e.g., revenue at risk, EBIT margin sensitivity).
    - For each major company, provide:
      * Topline revenue, EBITDA, and profit margins (latest available)
      * Geographic distribution of production and sales, with a focus on tariff-exposed flows
      * Quantitative estimate of tariff impact on P&L, cash flow, and balance sheet
      * Strategic options and likely management responses (e.g., supply chain reconfiguration, pricing actions, M&A)
    - Distinguish between companies likely to benefit and those likely to be harmed, and discuss potential for market share shifts.
    
    Use advanced financial analysis, cite all data sources, and discuss key uncertainties and scenario outcomes. Provide actionable recommendations for investors and policymakers.
    """

def get_major_company_list_prompt(investigation: dict) -> str:
    """Get the company list prompt for step 1 of company impact analysis, refined for expert-level analysis."""
    base_info = get_base_investigation_info(investigation)
    base_company_list_prompt = get_base_company_list_prompt()
    
    return f"""
    {base_info}
    
    Provide a comprehensive, data-driven list of major US and overseas companies that could be impacted by this investigation. Assume the reader is a market specialist.
    
    Focus on:
    1. **Well-known major players in the industry**
    2. **Any product lines from well known players that are impacted by the investigation which cannot easily be replaced because it is only produced in the US or in countries potentially subject to tariffs or restrictions resulting from the investigation**
    
    Ignore: 
    1. **Lesser-known but critical companies** that could act as bottlenecks
    2. **Sole-source or near-sole-source suppliers of products that will be impacted by the investigation**
    3. **Companies with specialized expertise or unique products**
    
    {base_company_list_prompt}
    
    For each company, provide explicit rationale for inclusion, cite data sources, and discuss any relevant caveats or uncertainties.
    """

def get_small_company_list_prompt(investigation: dict) -> str:
    """Get the company list prompt for step 2 of company impact analysis, refined for expert-level analysis."""
    base_info = get_base_investigation_info(investigation)
    base_company_list_prompt = get_base_company_list_prompt()
    
    return f"""
    {base_info}
    
    Provide a list of major US and overseas companies that could be impacted by this investigation, with a focus on supply chain bottlenecks and specialized players. Assume the reader is a market specialist.
    
    Focus on:
    1. **Lesser-known but critical companies** that could act as bottlenecks
    2. **Sole-source or near-sole-source suppliers of products that will be impacted by the investigation**
    3. **Companies with specialized expertise or unique products**
    
    Ignore: 
    1. **Well-known major players** in the industry
    2. **Companies that produce commoditized products that can easily be replaced**
    
    {base_company_list_prompt}
    
    For each company, provide explicit rationale for inclusion, cite data sources, and discuss any relevant caveats or uncertainties.
    """

def get_base_company_list_prompt() -> str:
    """Get the base company list prompt, refined for expert-level analysis."""
    
    return f"""
    For each company, provide:
    - Company name
    - Country/region of primary operations
    - Approximate annual revenue (in USD)
    - Portion of revenue that could be impacted by this investigation (as a percentage)
    - Brief description of their role in the supply chain
    - Whether they are US-only, overseas-only, or global
    
    Please include at least 15-20 companies, with a mix of large and small players. Focus on companies that would be most significantly affected by tariffs or trade restrictions.
    
    Use quantitative data where possible, cite sources, and highlight any data limitations or uncertainties.
    """

def get_company_json_prompt(company_list: str) -> str:
    """Get the prompt to convert company list to JSON format (no change needed for expert audience)."""
    return f"""
    Please convert the following company list into a valid JSON array format.
    
    Each company should be represented as a JSON object with these exact fields:
    - "name": Company name (string)
    - "country": Country/region of primary operations (string)
    - "revenue": Approximate annual revenue in USD (number, no commas or currency symbols)
    - "revenue_impact_percentage": Portion of revenue that could be impacted (number, no % symbol)
    - "description": Brief description of their role in the supply chain (string)
    - "geographic_scope": "US-only", "overseas-only", or "global" (string)
    
    Company list:
    {company_list}
    
    IMPORTANT: Return ONLY the JSON array, no additional text, no explanations, no markdown formatting.
    The response should start with [ and end with ].
    
    Example format:
    [
      {{
        "name": "Company Name",
        "country": "United States",
        "revenue": 1000000000,
        "revenue_impact_percentage": 25,
        "description": "Description of role",
        "geographic_scope": "US-only"
      }}
    ]
    """

def get_individual_company_analysis_prompt(investigation: dict, company_info: dict) -> str:
    """Get the prompt for individual company analysis, refined for expert-level analysis and concise, non-repetitive output under 2 pages."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    Write an equity research report style analysis of how {company_info['name']} would be impacted by potential tariffs or restrictions from the following US Government investigation. Assume the reader is a senior analyst or institutional investor.
    {base_info}
        
    Company Information:
    - Name: {company_info['name']}
    - Country: {company_info['country']}
    - Role: {company_info['description']}
    
    Please provide a comprehensive, data-driven analysis including:
    
    1. **Current Business Model:**
    - Primary products/services
    - Key customers and markets
    - Supply chain dependencies
    - Competitive position (reference Porter’s Five Forces or similar frameworks)
    
    2. **Direct Impact Assessment:**
    - How tariffs would affect their specific products/services
    - Provide information on where materials and products supporting 
    - Potential for passing costs to customers
    
    3. **Strategic Response Options:**
    - Potential business model adjustments
    - Supply chain diversification strategies
    - Geographic expansion or contraction
    - Product/service modifications
    
    4. **Risk Factors:**
    - Vulnerability to supply chain disruptions
    - Dependence on specific markets or customers
    - Regulatory or compliance challenges
    - Competitive threats or opportunities
    
    5. **Long-term Implications:**
    - Potential for market share gains or losses
    - Investment and expansion opportunities
    - Strategic partnerships or acquisitions
    - Innovation and R&D implications
    
    **IMPORTANT:**
    - Make sure you give specific examples of how this specific company would be impacted and how their
    products in particular would be impacted.
    - The entire report must be concise and fit within 2 printed pages (front and back of a single sheet).
    - Use precise, direct language and avoid unnecessary elaboration.
    - Do not repeat points or restate information in multiple sections.
    - Use bullet points or short paragraphs where appropriate for clarity.
    - Use advanced financial analysis, cite all data sources, and discuss key uncertainties and scenario outcomes. Provide actionable recommendations for investors and management.
    """

def get_additional_considerations_prompt(investigation: dict) -> str:
    """Get the additional considerations prompt, refined for expert-level analysis."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Provide ADDITIONAL CONSIDERATIONS for an expert audience, including:
    - Potential retaliatory measures (quantify where possible)
    - Impact on related industries and value chains (use input-output analysis if relevant)
    - Long-term strategic implications for US and global market structure
    - Regulatory and compliance considerations, including potential for non-tariff barriers
    
    Provide specific data, estimates, and cite sources. Discuss scenario outcomes, uncertainties, and implications for policymakers and investors.
    """

def get_supply_chain_bottlenecks_prompt(investigation: dict) -> str:
    """Get the supply chain bottlenecks and small companies prompt, refined for expert-level analysis."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Provide a detailed, data-driven SUPPLY CHAIN BOTTLENECKS AND SMALL COMPANIES ANALYSIS for an expert audience:
    
    Focus on identifying smaller companies and downstream suppliers that could act as critical bottlenecks in the supply chain:
    
    1. **Critical Small Suppliers:**
    - Identify smaller companies (under $1B revenue) that produce specialized components, materials, or services
    - Companies that are sole-source or near-sole-source suppliers for critical components
    - Suppliers of rare materials, specialized chemicals, or unique manufacturing processes
    - Companies with long lead times or limited production capacity
    
    2. **Market Share Opportunities:**
    - Small companies that could gain market share if larger competitors face tariff impacts
    - Domestic suppliers that could expand to fill gaps left by foreign suppliers
    - Companies in related industries that could pivot to serve the affected market
    - Startups or emerging companies with relevant technology or capabilities
    
    3. **Overseas-Only Suppliers:**
    - Companies that only exist in overseas markets and would receive tariff exceptions
    - Suppliers of components that cannot be easily sourced domestically
    - Companies that would face drastically increased costs due to tariffs
    - Suppliers in countries likely to be exempt from tariffs (e.g., allies, FTA partners)
    
    4. **Bottleneck Analysis:**
    - Components or materials with limited global supply
    - Manufacturing processes with specialized equipment or expertise requirements
    - Suppliers with long qualification processes or certification requirements
    - Companies with geographic concentration that could be disrupted
    
    5. **Impact Assessment:**
    - How tariffs would affect these smaller players (quantitative where possible)
    - Potential for supply chain disruption from small supplier failures
    - Opportunities for domestic small business growth
    - Risks of increased costs or delays from small supplier dependencies
    
    For each identified company, provide:
    - Company name and location
    - Products/services provided
    - Estimated revenue size (if known)
    - Why they are critical to the supply chain
    - Potential impact of tariffs on their business
    - Whether they would benefit, be harmed, or face exceptions
    
    Use quantitative data, cite sources, and discuss scenario outcomes and uncertainties. Provide actionable insights for supply chain strategists and policymakers.
    """

def get_all_prompts(investigation: dict) -> dict:
    """Get all prompts for an investigation."""
    return {
        'market_assessment': get_market_assessment_prompt(investigation),
        'tariff_impact': get_tariff_impact_prompt(investigation),
        'company_impact': get_company_impact_prompt(investigation),
        'supply_chain_bottlenecks': get_supply_chain_bottlenecks_prompt(investigation),
        'additional_considerations': get_additional_considerations_prompt(investigation)
    } 