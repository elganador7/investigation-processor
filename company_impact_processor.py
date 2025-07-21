import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from prompts import (
    get_major_company_list_prompt, 
    get_small_company_list_prompt,
    get_company_json_prompt, 
    get_individual_company_analysis_prompt
)
import google.genai as genai
from google.genai import types

# Load environment variables
load_dotenv()

class CompanyImpactProcessor:
    def __init__(self, use_gemini=True):
        self.use_gemini = use_gemini
        
        if use_gemini:
            try:
                self.gemini_api_key = os.getenv('GEMINI_API_KEY')
                if not self.gemini_api_key:
                    raise ValueError("GEMINI_API_KEY environment variable is required")
                
                # Initialize Gemini client
                self.gemini_client = genai.Client(
                    api_key=os.environ.get("GEMINI_API_KEY"),
                )
                self.model = 'gemini-2.5-flash-preview-05-20'
            except ImportError:
                raise ImportError("google-genai library is required for Gemini processing")
        else:
            self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
            if not self.perplexity_api_key:
                raise ValueError("PERPLEXITY_API_KEY environment variable is required")
            
            # Initialize OpenAI client with Perplexity API
            self.client = OpenAI(
                api_key=self.perplexity_api_key,
                base_url="https://api.perplexity.ai"
            )
    
    def call_api(self, prompt: str, investigation_title: str, enable_search=True) -> Dict[str, Any]:
        """Make API call with error handling and retries."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.use_gemini:
                    contents = [
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=prompt),
                            ],
                        ),
                    ]
                    generate_content_config = types.GenerateContentConfig(
                        response_mime_type="text/plain",
                        temperature=0.1,
                    )
                    
                    response = self.gemini_client.models.generate_content(
                        model=self.model,
                        contents=contents,
                        config=generate_content_config,
                    )
                    
                    if response.text:
                        return {
                            'success': True,
                            'content': response.text,
                            'investigation': investigation_title,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        raise Exception("No content in response")
                else:
                    response = self.client.chat.completions.create(
                        model="sonar-pro",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=4000,
                        temperature=0.1
                    )
                    
                    if response.choices and len(response.choices) > 0:
                        return {
                            'success': True,
                            'content': response.choices[0].message.content,
                            'investigation': investigation_title,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        raise Exception("No content in response")
                        
            except Exception as e:
                print(f"API call failed for {investigation_title} (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'investigation': investigation_title,
                        'timestamp': datetime.now().isoformat()
                    }
        
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'investigation': investigation_title,
            'timestamp': datetime.now().isoformat()
        }
    
    def step1a_generate_company_list(self, investigation: Dict[str, str]) -> Dict[str, Any]:
        """Step 1: Generate comprehensive list of companies."""
        print(f"Step 1: Generating company list for {investigation['title']}")
        
        prompt = get_major_company_list_prompt(investigation)
        result = self.call_api(prompt, investigation['title'], enable_search=True)
        
        return result
    
    def step1b_generate_company_list(self, investigation: Dict[str, str]) -> Dict[str, Any]:
        """Step 1: Generate comprehensive list of companies."""
        print(f"Step 1: Generating company list for {investigation['title']}")
        
        prompt = get_small_company_list_prompt(investigation)
        result = self.call_api(prompt, investigation['title'], enable_search=True)
        
        return result
    
    def step2_convert_to_json(self, company_list_content: str, investigation_title: str) -> Dict[str, Any]:
        """Step 2: Convert company list to JSON format."""
        print(f"Step 2: Converting company list to JSON for {investigation_title}")
        
        prompt = get_company_json_prompt(company_list_content)
        result = self.call_api(prompt, investigation_title, enable_search=False)
        
        if result['success']:
            try:
                # Debug: print the raw response
                print(f"Raw API response: {result['content'][:200]}...")
                
                # Try to parse the JSON to validate it
                companies = json.loads(result['content'])
                result['parsed_companies'] = companies
                print(f"Successfully parsed {len(companies)} companies")
            except json.JSONDecodeError as e:
                result['success'] = False
                result['error'] = f"Failed to parse JSON: {str(e)}"
                print(f"JSON parsing failed: {str(e)}")
                print(f"Full response content: {result['content']}")
        
        return result
    
    def step3_generate_individual_reports(self, investigation: Dict[str, str], companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Step 3: Generate individual company reports."""
        print(f"Step 3: Generating individual company reports for {investigation['title']}")
        
        results = []
        
        for i, company in enumerate(companies):
            print(f"  Processing company {i+1}/{len(companies)}: {company['name']}")
            
            prompt = get_individual_company_analysis_prompt(investigation, company)
            result = self.call_api(prompt, f"{investigation['title']} - {company['name']}", enable_search=True)
            
            # Add company info to result
            result['company_info'] = company
            
            results.append(result)
            
            # Add delay between API calls
            if i < len(companies) - 1:
                time.sleep(2)
        
        return results
    
    def process_investigation(self, investigation: Dict[str, str]) -> Dict[str, Any]:
        """Process a single investigation through all three steps."""
        print(f"\nProcessing investigation: {investigation['title']}")
        
        # Step 1: Generate company list
        step1a_result = self.step1a_generate_company_list(investigation, 'major')
        if not step1a_result['success']:
            return {
                'investigation': investigation['title'],
                'timestamp': datetime.now().isoformat(),
                'investigation_data': investigation,
                'success': False,
                'error': f"Step 1 failed: {step1a_result['error']}"
            }
            
        step1b_result = self.step1b_generate_company_list(investigation, 'small')
        if not step1b_result['success']:
            return {
                'investigation': investigation['title'],
                'timestamp': datetime.now().isoformat(),
                'investigation_data': investigation,
                'step1_result': step1b_result,
                'success': False,
                'error': f"Step 1 failed: {step1b_result['error']}"
            }
        
        # Step 2: Convert to JSON
        step2_result = self.step2_convert_to_json(step1a_result['content'] + step1b_result['content'], investigation['title'])
        if not step2_result['success']:
            return {
                'investigation': investigation['title'],
                'timestamp': datetime.now().isoformat(),
                'investigation_data': investigation,
                'step1_result': step1a_result,
                'success': False,
                'error': f"Step 2 failed: {step2_result['error']}"
            }
        
        # Step 3: Generate individual reports
        companies = step2_result['parsed_companies']
        step3_results = self.step3_generate_individual_reports(investigation, companies)
        
        # Compile final result
        final_result = {
            'investigation': investigation['title'],
            'timestamp': datetime.now().isoformat(),
            'investigation_data': investigation,
            'step1a_company_list': step1a_result,
            'step1b_company_list': step1b_result,
            'step2_json_conversion': step2_result,
            'step3_individual_reports': step3_results,
            'total_companies': len(companies),
            'success': True
        }
        
        return final_result
    
    def save_results(self, results: Dict[str, Any], base_filename: str = None):
        """Save results to JSON file."""
        if not base_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"company_impact_analysis_{timestamp}"
        
        # Save main results file
        main_filename = f"{base_filename}.json"
        with open(main_filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Main results saved to {main_filename}")
        
        # Create folder structure for individual reports
        folder_name = f"{base_filename}_reports"
        os.makedirs(folder_name, exist_ok=True)
        
        # Save individual company reports
        if results.get('success') and 'step3_individual_reports' in results:
            for i, report in enumerate(results['step3_individual_reports']):
                if report['success']:
                    company_name = report['company_info']['name']
                    # Clean filename
                    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_name = safe_name.replace(' ', '_')
                    
                    report_filename = f"{folder_name}/{i+1:02d}_{safe_name}_analysis.md"
                    
                    # Convert to markdown format
                    markdown_content = self._convert_report_to_markdown(report, results['investigation'])
                    
                    with open(report_filename, 'w') as f:
                        f.write(markdown_content)
                    
                    print(f"  Company report saved: {report_filename}")
        
        # Create overview report
        overview_filename = f"{folder_name}/00_OVERVIEW_ANALYSIS.md"
        overview_content = self._generate_overview_report(results)
        
        with open(overview_filename, 'w') as f:
            f.write(overview_content)
        
        print(f"Overview report saved: {overview_filename}")
        
        return main_filename, folder_name
    
    def _convert_report_to_markdown(self, report: Dict[str, Any], investigation_title: str) -> str:
        """Convert individual company report to markdown format."""
        company = report['company_info']
        
        markdown = f"""# Company Impact Analysis: {company['name']}

**Investigation:** {investigation_title}  
**Analysis Date:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}  
**AI Model:** {'Google Gemini AI' if self.use_gemini else 'Perplexity AI'}

---

## Company Overview

- **Name:** {company['name']}
- **Country:** {company['country']}
- **Annual Revenue:** ${company['revenue']:,}
- **Revenue Impact Potential:** {company['revenue_impact_percentage']}%
- **Geographic Scope:** {company['geographic_scope']}
- **Role:** {company['description']}

---

## Detailed Analysis

{report['content']}

---

*This analysis was generated using {'Google Gemini AI' if self.use_gemini else 'Perplexity AI'} and represents a comprehensive assessment of the potential impacts of trade restrictions on {company['name']}.*
"""
        
        return markdown
    
    def _generate_overview_report(self, results: Dict[str, Any]) -> str:
        """Generate overview report for all companies."""
        investigation_title = results['investigation']
        companies = results['step2_json_conversion']['parsed_companies']
        
        # Calculate statistics
        total_revenue = sum(c['revenue'] for c in companies)
        avg_impact_percentage = sum(c['revenue_impact_percentage'] for c in companies) / len(companies)
        
        us_companies = [c for c in companies if c['geographic_scope'] == 'US-only']
        overseas_companies = [c for c in companies if c['geographic_scope'] == 'overseas-only']
        global_companies = [c for c in companies if c['geographic_scope'] == 'global']
        
        markdown = f"""# Company Impact Analysis Overview

**Investigation:** {investigation_title}  
**Analysis Date:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}  
**AI Model:** {'Google Gemini AI' if self.use_gemini else 'Perplexity AI'}

---

## Executive Summary

This analysis examines the potential impact of trade restrictions on {len(companies)} companies identified as key players in the {investigation_title.lower()} supply chain.

### Key Statistics

- **Total Companies Analyzed:** {len(companies)}
- **Combined Annual Revenue:** ${total_revenue:,.0f}
- **Average Revenue Impact Potential:** {avg_impact_percentage:.1f}%
- **US-Only Companies:** {len(us_companies)}
- **Overseas-Only Companies:** {len(overseas_companies)}
- **Global Companies:** {len(global_companies)}

---

## Company Categories

### US-Only Companies ({len(us_companies)})

These companies operate exclusively within the United States and could benefit from trade restrictions:

"""
        
        for company in us_companies:
            markdown += f"- **{company['name']}** ({company['country']}) - ${company['revenue']:,} revenue, {company['revenue_impact_percentage']}% impact potential\n"
        
        markdown += "\n### Overseas-Only Companies ({len(overseas_companies)})\n\n"
        markdown += "These companies operate exclusively outside the United States and could face significant challenges:\n\n"
        
        for company in overseas_companies:
            markdown += f"- **{company['name']}** ({company['country']}) - ${company['revenue']:,} revenue, {company['revenue_impact_percentage']}% impact potential\n"
        
        markdown += "\n### Global Companies ({len(global_companies)})\n\n"
        markdown += "These companies operate globally and may have mixed impacts:\n\n"
        
        for company in global_companies:
            markdown += f"- **{company['name']}** ({company['country']}) - ${company['revenue']:,} revenue, {company['revenue_impact_percentage']}% impact potential\n"
        
        markdown += f"""

---

## Analysis Methodology

This analysis was conducted in three steps:

1. **Company Identification:** Comprehensive list of companies that could be impacted by the investigation
2. **Data Structuring:** Conversion of company information to structured format
3. **Individual Analysis:** Detailed impact assessment for each identified company

## Individual Reports

Detailed analysis for each company is available in separate files within this folder:

"""
        
        for i, company in enumerate(companies):
            safe_name = "".join(c for c in company['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            markdown += f"{i+1:02d}. [{company['name']}]({i+1:02d}_{safe_name}_analysis.md)\n"
        
        markdown += f"""

---

*This overview was generated from AI-powered analysis of {len(companies)} companies identified as key players in the {investigation_title.lower()} supply chain.*
"""
        
        return markdown

def main():
    """Main execution function."""
    try:
        # Load investigation data
        with open('ongoing_investigations.json', 'r') as f:
            investigations = json.load(f)
        
        # Process first investigation as example
        investigation = investigations[0]
        
        # Initialize processor (using Gemini by default)
        processor = CompanyImpactProcessor(use_gemini=True)
        
        # Process the investigation
        results = processor.process_investigation(investigation)
        
        # Save results
        processor.save_results(results)
        
        print("\nCompany impact analysis complete! Check the generated files for results.")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    main() 