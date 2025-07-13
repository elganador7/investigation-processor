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
    - Current import volumes and values
    - Portion of the market that would be subject to tariffs if enacted
    - Key market players and their market shares
    - Current trade patterns and major exporting countries
    
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