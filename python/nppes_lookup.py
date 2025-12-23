"""
============================================================================
NPPES PROVIDER LOOKUP TOOL
============================================================================
PURPOSE: Automate the retrieval of provider information from CMS's National
         Plan and Provider Enumeration System (NPPES) Registry.

BUSINESS CONTEXT: When new provider NPIs appear in eligibility files but 
         aren't in our reference tables, someone has to manually look them
         up one by one. This script automates that process.

HOW IT WORKS:
    1. Takes a list of NPI numbers
    2. Queries the public NPPES API for each one
    3. Extracts key demographics (name, address, specialty, etc.)
    4. Outputs a clean Excel file ready for CRM import

API DOCUMENTATION: https://npiregistry.cms.hhs.gov/api-page
============================================================================
"""

import requests
import pandas as pd
import time


def lookup_npi(npi: str) -> dict:
    """
    Query the NPPES API for a single NPI number.
    
    Args:
        npi: 10-digit National Provider Identifier
        
    Returns:
        Dictionary containing provider demographics or error status
        
    Note:
        The NPPES API is public and free but we add delays between
        calls to be respectful of their servers.
    """
    url = f"https://npiregistry.cms.hhs.gov/api/?number={npi}&version=2.1"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # API returns result_count=0 if NPI doesn't exist
        if data.get('result_count', 0) == 0:
            return {'ProviderNpi': npi, 'Status': 'NOT_FOUND'}
        
        # Extract the provider record
        result = data['results'][0]
        basic = result.get('basic', {})
        addresses = result.get('addresses', [])
        taxonomies = result.get('taxonomies', [])
        
        # Get practice location (prefer LOCATION over MAILING address)
        # The API returns multiple addresses - we want where they actually practice
        practice_addr = next(
            (a for a in addresses if a.get('address_purpose') == 'LOCATION'),
            addresses[0] if addresses else {}
        )
        
        # Get primary taxonomy (specialty)
        # Providers can have multiple specialties - grab the primary one
        primary_tax = next(
            (t for t in taxonomies if t.get('primary')),
            taxonomies[0] if taxonomies else {}
        )
        
        # Build clean output record
        # Note: 'last_name' is empty for organizations, so we fall back to org name
        return {
            'ProviderNpi': npi,
            'FirstName': basic.get('first_name', ''),
            'LastName': basic.get('last_name', '') or basic.get('organization_name', ''),
            'Address': practice_addr.get('address_1', ''),
            'City': practice_addr.get('city', ''),
            'State': practice_addr.get('state', ''),
            'ZipCode': practice_addr.get('postal_code', '')[:5] if practice_addr.get('postal_code') else '',
            'Phone': practice_addr.get('telephone_number', ''),
            'ProviderType': primary_tax.get('desc', ''),
            'Status': 'SUCCESS'
        }
        
    except Exception as e:
        # Catch network errors, JSON parsing issues, etc.
        # We return error status instead of crashing so batch can continue
        return {'ProviderNpi': npi, 'Status': f'ERROR: {str(e)}'}


def process_batch(npi_list: list, output_file: str = 'providers.xlsx') -> pd.DataFrame:
    """
    Process multiple NPIs and save results to Excel.
    
    Args:
        npi_list: List of NPI numbers to look up
        output_file: Path for output Excel file
        
    Returns:
        DataFrame containing all lookup results
        
    Note:
        Includes 0.3 second delay between API calls to avoid
        overwhelming the NPPES servers. Be a good API citizen!
    """
    providers = []
    
    for i, npi in enumerate(npi_list, 1):
        result = lookup_npi(npi)
        providers.append(result)
        
        # Progress indicator (helpful for large batches)
        status = "✓" if result['Status'] == 'SUCCESS' else "✗"
        print(f"{status} [{i}/{len(npi_list)}] {npi}")
        
        # Rate limiting - be respectful of the free public API
        time.sleep(0.3)
    
    # Convert to DataFrame and save
    df = pd.DataFrame(providers)
    df.to_excel(output_file, index=False)
    print(f"\n✓ Saved to {output_file}")
    
    return df


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
# To use this script:
#   1. Replace the sample NPI below with your list of NPIs
#   2. Run: python nppes_lookup.py
#   3. Check the output Excel file
#
# For large batches, you can read NPIs from a file:
#   npis = pd.read_csv('npi_list.csv')['npi'].tolist()
#   process_batch(npis, 'provider_results.xlsx')
# ============================================================================

if __name__ == '__main__':
    # Example: Look up a single NPI (replace with your actual NPIs)
    npis = ['1234567890']  # Replace with your NPIs
    process_batch(npis)
