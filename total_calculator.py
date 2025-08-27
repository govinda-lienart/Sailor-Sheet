# =============================================================================
# TOTAL CALCULATOR
# Purpose: Handle all total calculation and management functions
# =============================================================================

def update_total_automatically(sheet):
    """
    Smart function that automatically manages totals
    - Always puts TOTAL at the very end
    - Updates existing TOTAL or creates new one
    - Never puts TOTAL in the middle of data
    """
    try:
        # Get all data from the sheet
        all_values = sheet.get_all_values()
        
        # Collect all transaction amounts (skip header and TOTAL rows)
        amounts = []
        transaction_count = 0
        
        for row in all_values:
            # Skip empty rows, header row, and TOTAL rows
            if (len(row) > 1 and 
                row[0] and row[1] and 
                'TOTAL' not in str(row[0]).upper() and
                str(row[0]).strip() != 'Name'):  # Skip header
                
                try:
                    # Clean and convert amount to float
                    cleaned_amount = str(row[1]).replace('$', '').replace('€', '').replace(',', '').strip()
                    if cleaned_amount and cleaned_amount.replace('.', '').replace('-', '').isdigit():
                        amounts.append(float(cleaned_amount))
                        transaction_count += 1
                except ValueError:
                    continue
        
        # Calculate total
        total = sum(amounts)
        
        # Find and delete ALL existing TOTAL rows first
        rows_to_delete = []
        for i, row in enumerate(all_values):
            if row[0] and 'TOTAL' in str(row[0]).upper():
                rows_to_delete.append(i + 1)  # +1 because sheet rows are 1-indexed
        
        # Delete TOTAL rows from bottom to top to avoid index issues
        for row_num in sorted(rows_to_delete, reverse=True):
            try:
                sheet.delete_rows(row_num)
            except:
                pass
        
        # Add new TOTAL row at the very end
        total_data = ['TOTAL', total, f'{transaction_count} transactions', '']
        sheet.append_row(total_data)
        
        return total
        
    except Exception as e:
        print(f"Error updating total: {e}")
        return None

def calculate_simple_total(amounts):
    """
    Calculate total from a list of amounts
    """
    try:
        return sum(float(amount) for amount in amounts if amount and amount.replace('.', '').replace('-', '').isdigit())
    except Exception as e:
        print(f"Error calculating total: {e}")
        return 0

def get_transaction_count(sheet):
    """
    Get the number of transactions in the sheet
    """
    try:
        all_values = sheet.get_all_values()
        # Count rows with actual data (skip header and total rows)
        data_rows = [row for row in all_values[1:] if row[0] and row[1] and 'TOTAL' not in row[0]]
        return len(data_rows)
    except Exception as e:
        print(f"Error getting transaction count: {e}")
        return 0
