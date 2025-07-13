"""
Shared prompt definitions for investigation analysis.
This module contains prompts that can be used by both Perplexity and Gemini processors.
"""

def get_base_investigation_info(investigation: dict) -> str:
    """Get the base investigation information for prompts."""
    return f"Investigation: {investigation['title']}\nDescription: {investigation['description']}"

def get_market_assessment_prompt(investigation: dict) -> str:
    """Get the market assessment prompt."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Please provide a detailed CURRENT MARKET ASSESSMENT including:
    - Total market size in USD (global and US market)
    - Current imports to and exports from the US in this sector.
    - Portion of the US market that would be subject to tariffs if enacted. 
    You should estimate any downstream supply chains that would be affected, even if they support US companies
    - Key market players and their market shares
    - Current trade patterns and major exporting and importing countries
    
    Please provide specific data, estimates, and cite sources where possible.
    """

def get_tariff_impact_prompt(investigation: dict) -> str:
    """Get the tariff impact analysis prompt."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Please provide a detailed TARIFF IMPACT ANALYSIS for each tariff rate (10%, 25%, 50%):
    - Estimated cost if current trade patterns remain unchanged
    - Assessment of US companies' ability to fill increased demand
    - Estimated shift in consumption to domestic markets
    - Impact on supply chains and production costs
    - Potential price increases for end consumers
    - Assessment of the impact to aggregate demand in the impacted market in the US.
    
    Please provide specific data, estimates, and cite sources where possible.
    """

def get_company_impact_prompt(investigation: dict) -> str:
    """Get the company impact analysis prompt."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Please provide a detailed COMPANY IMPACT ANALYSIS:
    - Identify major companies likely to be impacted (both US and foreign)
    - For each major company, provide:
      * Topline revenue and profit margins
      * Geographic distribution of production
      * Estimated impact of tariffs on their operations
      * Potential strategies they might employ
    - Include both companies that would benefit and those that would be harmed
    
    Please provide specific data, estimates, and cite sources where possible.
    """

def get_company_list_prompt(investigation: dict) -> str:
    """Get the company list prompt for step 1 of company impact analysis."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Please provide a comprehensive list of US and overseas companies that could be impacted by this investigation.
    
    Focus on:
    1. **Well-known major players** in the industry
    2. **Lesser-known but critical companies** that could act as bottlenecks
    3. **Companies that exist only in either the US or abroad** (not both)
    4. **Sole-source or near-sole-source suppliers**
    5. **Companies with specialized expertise or unique products**
    
    For each company, provide:
    - Company name
    - Country/region of primary operations
    - Approximate annual revenue (in USD)
    - Portion of revenue that could be impacted by this investigation (as a percentage)
    - Brief description of their role in the supply chain
    - Whether they are US-only, overseas-only, or global
    
    Please include at least 15-20 companies, with a mix of large and small players.
    Focus on companies that would be most significantly affected by tariffs or trade restrictions.
    """

def get_company_json_prompt(company_list: str) -> str:
    """Get the prompt to convert company list to JSON format."""
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
    """Get the prompt for individual company analysis."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Please provide a detailed analysis of how {company_info['name']} would be impacted by potential tariffs or restrictions from this investigation.
    
    Company Information:
    - Name: {company_info['name']}
    - Country: {company_info['country']}
    - Annual Revenue: ${company_info['revenue']:,}
    - Revenue Impact Potential: {company_info['revenue_impact_percentage']}%
    - Role: {company_info['description']}
    - Geographic Scope: {company_info['geographic_scope']}
    
    Please provide a comprehensive analysis including:
    
    1. **Current Business Model:**
    - Primary products/services
    - Key customers and markets
    - Supply chain dependencies
    - Competitive position
    
    2. **Direct Impact Assessment:**
    - How tariffs would affect their specific products/services
    - Estimated cost increases or revenue losses
    - Impact on profit margins
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
    
    Please provide specific data, estimates, and actionable insights where possible.
    """

def get_additional_considerations_prompt(investigation: dict) -> str:
    """Get the additional considerations prompt."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Please provide ADDITIONAL CONSIDERATIONS including:
    - Potential retaliatory measures
    - Impact on related industries
    - Long-term strategic implications
    - Regulatory and compliance considerations
    
    Please provide specific data, estimates, and cite sources where possible.
    """

def get_supply_chain_bottlenecks_prompt(investigation: dict) -> str:
    """Get the supply chain bottlenecks and small companies prompt."""
    base_info = get_base_investigation_info(investigation)
    
    return f"""
    {base_info}
    
    Please provide a detailed SUPPLY CHAIN BOTTLENECKS AND SMALL COMPANIES ANALYSIS:
    
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
    - How tariffs would affect these smaller players
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
    
    Please provide specific examples, estimates, and cite sources where possible.
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