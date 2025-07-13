#!/usr/bin/env python3
"""
Utility script to convert investigation results JSON files into markdown documents.
This script can process both single investigation results and full investigation batches.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

class InvestigationMarkdownGenerator:
    def __init__(self, json_file_path: str):
        """Initialize the generator with a JSON file path."""
        self.json_file_path = json_file_path
        self.data = self._load_json_data()
        
    def _load_json_data(self) -> Any:
        """Load and parse the JSON data."""
        try:
            with open(self.json_file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {self.json_file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    
    def _format_timestamp(self, timestamp_str: str) -> str:
        """Format timestamp string for display."""
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return timestamp_str
    
    def _extract_market_data(self, content: str) -> Dict[str, str]:
        """Extract key market data from content."""
        market_data = {}
        
        # Look for market size patterns
        import re
        
        # Market size patterns
        market_size_patterns = [
            r'\$[\d,]+\.?\d*\s*(?:billion|million|trillion)',
            r'[\d,]+\.?\d*\s*(?:billion|million|trillion)\s*(?:USD|dollars)',
        ]
        
        market_sizes = []
        for pattern in market_size_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            market_sizes.extend(matches)
        
        if market_sizes:
            market_data['market_sizes'] = market_sizes[:5]  # Top 5
        
        # Company mentions
        company_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc|Corp|LLC|Ltd|Company|Co|SE|Holdings)',
            r'(?:company|firm|manufacturer)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        companies = set()
        for pattern in company_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            companies.update(matches)
        
        if companies:
            market_data['companies'] = list(companies)[:10]  # Top 10
        
        return market_data
    
    def _generate_single_investigation_markdown(self, investigation_data: Dict[str, Any]) -> str:
        """Generate markdown for a single investigation."""
        title = investigation_data['investigation']
        timestamp = investigation_data['timestamp']
        investigation_info = investigation_data['investigation_data']
        analysis_sections = investigation_data.get('analysis_sections', {})
        
        # Determine if this is a Gemini or Perplexity result
        is_gemini = 'analysis_sections' in investigation_data
        
        markdown = f"""# {title}: Section 232 Investigation Analysis

**Generated:** {self._format_timestamp(timestamp)}  
**Source:** {investigation_info['source']}  
**Analysis Method:** {'Google Gemini AI' if is_gemini else 'Perplexity AI'}

---

## Executive Summary

This analysis examines the potential impacts of a Section 232 investigation into imports of {title.lower()} on U.S. national security. The investigation, initiated under the Trade Expansion Act of 1962, could lead to tariffs or other trade restrictions on these critical products.

**Investigation Description:** {investigation_info['description']}

"""
        
        # Add market data summary if available
        if analysis_sections:
            market_assessment = analysis_sections.get('market_assessment', {})
            if 'content' in market_assessment:
                market_data = self._extract_market_data(market_assessment['content'])
                if market_data:
                    markdown += "**Key Market Insights:**\n"
                    if 'market_sizes' in market_data:
                        markdown += f"- **Market Sizes Identified:** {', '.join(market_data['market_sizes'])}\n"
                    if 'companies' in market_data:
                        markdown += f"- **Key Companies Mentioned:** {', '.join(market_data['companies'])}\n"
                    markdown += "\n"
        
        markdown += "---\n\n"
        
        # Process each analysis section
        section_order = ['market_assessment', 'tariff_impact', 'company_impact', 'supply_chain_bottlenecks', 'additional_considerations']
        
        for i, section_name in enumerate(section_order):
            if section_name in analysis_sections:
                section_data = analysis_sections[section_name]
                
                if 'content' in section_data:
                    # Format section title
                    section_title = section_name.replace('_', ' ').title()
                    markdown += f"## {i+1}. {section_title}\n\n"
                    
                    # Add section content
                    content = section_data['content']
                    
                    # Clean up the content formatting
                    content = self._clean_content_formatting(content)
                    
                    markdown += content + "\n\n"
                    
                    # Add section timestamp if available
                    if 'timestamp' in section_data:
                        markdown += f"*Analysis completed: {self._format_timestamp(section_data['timestamp'])}*\n\n"
                    
                    markdown += "---\n\n"
                else:
                    # Handle error in section
                    markdown += f"## {i+1}. {section_name.replace('_', ' ').title()}\n\n"
                    markdown += f"**Error:** {section_data.get('error', 'Unknown error occurred')}\n\n"
                    markdown += "---\n\n"
        
        # Add conclusion
        markdown += """## Conclusion

This analysis provides a comprehensive assessment of the potential impacts of Section 232 tariffs on """ + title.lower() + """ imports. The investigation represents a significant trade action with far-reaching implications for the industry, supply chains, and international trade relationships.

Key considerations include:
- **Market Impact:** Effects on pricing, supply, and competition
- **Company Effects:** Winners and losers from tariff implementation  
- **Supply Chain Bottlenecks:** Critical small suppliers and potential disruption points
- **Supply Chain Disruption:** Impacts on global manufacturing networks
- **Retaliation Risk:** Potential countermeasures from trading partners
- **Strategic Implications:** Long-term effects on industry structure and innovation

Any trade actions should be carefully calibrated to balance legitimate security concerns with the economic and strategic benefits of international cooperation.

---

*This analysis was generated using """ + ('Google Gemini AI' if is_gemini else 'Perplexity AI') + """ and represents a comprehensive assessment of the potential impacts of Section 232 tariffs on """ + title.lower() + """ imports. The analysis incorporates market data, company financials, and industry trends to provide a detailed evaluation of the economic and strategic implications.*"""
        
        return markdown
    
    def _generate_batch_investigation_markdown(self, investigations_data: List[Dict[str, Any]]) -> str:
        """Generate markdown for a batch of investigations."""
        successful_results = [r for r in investigations_data if r.get('success', True)]
        failed_results = [r for r in investigations_data if not r.get('success', True)]
        
        markdown = f"""# Investigation Analysis Summary Report

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}  
**Source File:** {os.path.basename(self.json_file_path)}  
**Total Investigations:** {len(investigations_data)}  
**Successful Analyses:** {len(successful_results)}  
**Failed Analyses:** {len(failed_results)}

---

## Executive Summary

This report summarizes the analysis of {len(investigations_data)} trade investigations using AI-powered market assessment tools. Each investigation was analyzed across five key dimensions:

1. **Market Assessment** - Current market size, trade patterns, and key players
2. **Tariff Impact Analysis** - Effects of 10%, 25%, and 50% tariffs
3. **Company Impact Analysis** - Winners, losers, and strategic responses
4. **Supply Chain Bottlenecks** - Critical small suppliers and potential disruption points
5. **Additional Considerations** - Retaliation, supply chains, and long-term implications

---

## Investigation Results

"""
        
        # Process successful investigations
        for i, result in enumerate(successful_results, 1):
            title = result['investigation']
            source = result['investigation_data']['source']
            
            markdown += f"### {i}. {title}\n\n"
            markdown += f"**Source:** {source}\n\n"
            
            # Add brief summary of each section
            analysis_sections = result.get('analysis_sections', {})
            for section_name, section_data in analysis_sections.items():
                if 'content' in section_data:
                    content = section_data['content']
                    # Extract first few sentences as summary
                    sentences = content.split('. ')
                    summary = '. '.join(sentences[:2]) + '.'
                    markdown += f"**{section_name.replace('_', ' ').title()}:** {summary}\n\n"
            
            markdown += "---\n\n"
        
        # Add failed investigations
        if failed_results:
            markdown += "## Failed Analyses\n\n"
            for result in failed_results:
                markdown += f"- **{result['investigation']}:** {', '.join(result.get('errors', [result.get('error', 'Unknown error')]))}\n"
            markdown += "\n"
        
        # Add summary statistics
        markdown += "## Summary Statistics\n\n"
        
        # Calculate average content length
        if successful_results:
            total_length = 0
            for result in successful_results:
                analysis_sections = result.get('analysis_sections', {})
                for section_data in analysis_sections.values():
                    if 'content' in section_data:
                        total_length += len(section_data['content'])
            
            avg_length = total_length / len(successful_results)
            markdown += f"- **Average Analysis Length:** {avg_length:,.0f} characters\n"
        
        markdown += f"- **Success Rate:** {(len(successful_results) / len(investigations_data) * 100):.1f}%\n"
        markdown += f"- **Analysis Method:** {'Google Gemini AI' if 'analysis_sections' in (successful_results[0] if successful_results else {}) else 'Perplexity AI'}\n"
        
        markdown += "\n---\n\n"
        
        markdown += """## Key Insights

This batch analysis reveals several important patterns across the investigated industries:

1. **Market Concentration:** Many industries show high concentration among key players
2. **Supply Chain Complexity:** Global supply chains create interdependencies that complicate tariff impacts
3. **Retaliation Risk:** Most investigations identify significant retaliation potential from trading partners
4. **Capacity Constraints:** U.S. manufacturers often lack capacity to fill demand created by import restrictions

## Recommendations

Based on the comprehensive analysis of these investigations:

1. **Targeted Approaches:** Consider narrowly focused measures rather than broad tariffs
2. **Alliance Coordination:** Work with key allies to address security concerns without triggering trade wars
3. **Investment Focus:** Prioritize domestic investment in manufacturing capacity over protectionist measures
4. **Supply Chain Resilience:** Develop strategies to strengthen critical supply chains without disrupting global cooperation

---

*This report was generated from AI-powered analysis of trade investigation data. Each individual investigation contains detailed market assessments, tariff impact analysis, and company-specific insights.*"""
        
        return markdown
    
    def _clean_content_formatting(self, content: str) -> str:
        """Clean up content formatting for better markdown presentation."""
        # Remove excessive newlines
        content = '\n'.join(line for line in content.split('\n') if line.strip())
        
        # Fix bullet points
        content = content.replace('•', '-')
        
        # Ensure proper spacing around headers
        content = content.replace('\n**', '\n\n**')
        
        return content
    
    def generate_markdown(self, output_file: Optional[str] = None) -> str:
        """Generate markdown content from the JSON data."""
        # Determine if this is a single investigation or batch
        if isinstance(self.data, list):
            # Batch of investigations
            markdown_content = self._generate_batch_investigation_markdown(self.data)
        else:
            # Single investigation
            markdown_content = self._generate_single_investigation_markdown(self.data)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(markdown_content)
            print(f"Markdown document saved to: {output_file}")
        
        return markdown_content

def main():
    """Main function to run the markdown generator."""
    parser = argparse.ArgumentParser(description='Convert investigation results JSON to markdown')
    parser.add_argument('json_file', help='Path to the JSON file to convert')
    parser.add_argument('-o', '--output', help='Output markdown file path (optional)')
    
    args = parser.parse_args()
    
    try:
        # Generate markdown
        generator = InvestigationMarkdownGenerator(args.json_file)
        
        # Determine output filename if not specified
        if not args.output:
            base_name = os.path.splitext(os.path.basename(args.json_file))[0]
            args.output = f"{base_name}_analysis.md"
        
        # Generate and save markdown
        markdown_content = generator.generate_markdown(args.output)
        
        print(f"Successfully converted {args.json_file} to markdown format")
        print(f"Output saved to: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 