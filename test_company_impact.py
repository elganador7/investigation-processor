#!/usr/bin/env python3
"""
Test script for the Company Impact Processor.
This script tests the three-step company impact analysis process.
"""

import json
import os
from company_impact_processor import CompanyImpactProcessor

def test_company_impact_analysis():
    """Test the company impact analysis process."""
    
    # Load investigation data
    with open('ongoing_investigations.json', 'r') as f:
        investigations = json.load(f)
    
    # Use the first investigation for testing
    investigation = investigations[0]
    print(f"Testing company impact analysis for: {investigation['title']}")
    
    try:
        # Initialize processor with Gemini
        processor = CompanyImpactProcessor(use_gemini=True)
        
        # Process the investigation through all three steps
        results = processor.process_investigation(investigation)
        
        if results['success']:
            print(f"\n✅ Analysis completed successfully!")
            print(f"Total companies analyzed: {results['total_companies']}")
            
            # Save results
            main_file, reports_folder = processor.save_results(results)
            print(f"\n📁 Results saved:")
            print(f"  Main file: {main_file}")
            print(f"  Reports folder: {reports_folder}")
            
            # Show summary of companies
            companies = results['step2_json_conversion']['parsed_companies']
            print(f"\n📊 Company Summary:")
            print(f"  Total companies: {len(companies)}")
            
            us_companies = [c for c in companies if c['geographic_scope'] == 'US-only']
            overseas_companies = [c for c in companies if c['geographic_scope'] == 'overseas-only']
            global_companies = [c for c in companies if c['geographic_scope'] == 'global']
            
            print(f"  US-only: {len(us_companies)}")
            print(f"  Overseas-only: {len(overseas_companies)}")
            print(f"  Global: {len(global_companies)}")
            
            # Show top companies by revenue impact
            sorted_companies = sorted(companies, key=lambda x: x['revenue_impact_percentage'], reverse=True)
            print(f"\n🏆 Top 5 companies by revenue impact potential:")
            for i, company in enumerate(sorted_companies[:5]):
                print(f"  {i+1}. {company['name']} ({company['country']}) - {company['revenue_impact_percentage']}%")
            
        else:
            print(f"\n❌ Analysis failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    test_company_impact_analysis() 