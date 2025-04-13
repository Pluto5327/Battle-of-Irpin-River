import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

class IrpinDataAnalyzer:
    """Class for analyzing battle data of the Irpin River."""
    
    def __init__(self, script_dir=None):
        if script_dir is None:
            self.script_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.script_dir = script_dir
        
        # Set the correct directory path
        self.output_dir = os.path.join(self.script_dir, "Uniform - with Artillery")
        
        # Check if output directory exists
        if not os.path.exists(self.output_dir):
            print(f"Warning: Output directory '{self.output_dir}' does not exist.")
            print(f"Current directory: {os.getcwd()}")
            print(f"Available directories: {[d for d in os.listdir(self.script_dir) if os.path.isdir(os.path.join(self.script_dir, d))]}")
        
        self.data = None
        self.statistics = {}

    def preprocess_csv_files(self, file1=None):
        if file1 is None:
            # Only look for table.csv files
            csv_files = []
            if os.path.exists(self.output_dir):
                for f in os.listdir(self.output_dir):
                    if f.endswith('-table.csv'):
                        csv_files.append(f)
            
            if csv_files:
                print(f"Available table CSV files in {self.output_dir}:")
                for i, csv_file in enumerate(csv_files, 1):
                    print(f"{i}. {csv_file}")
                
                # Use the table CSV file
                file1 = os.path.join(self.output_dir, csv_files[0])
                print(f"Using file: {file1}")
            else:
                file1 = os.path.join(self.output_dir, "IrpinModel Vary Site-Selection Artillery Active-table.csv")
                print(f"No table CSV files found, attempting to use default: {file1}")
        
        print("Starting CSV file preprocessing.")
        try:
            # Try different skiprows values if needed
            T = pd.read_csv(file1, skiprows=6)
            print("File successfully loaded.")
            
            # Debug: Display actual column names
            print("\nActual columns in the loaded CSV:")
            print(T.columns.tolist())
            
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            self._inspect_csv_files([file1])
            return False

        T = self._standardize_column_names(T)
        self.data = T

        print("----- Preprocessed Data (Head) -----")
        print(self.data.head())
        
        # Additional check to ensure required columns exist
        required_columns = ['site_selection_mode', 'battle_outcome', 
                           'total_infantry_casualties_10', 'total_infantry_used', 
                           'total_infantry_crossed']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        
        if missing_columns:
            print(f"Warning: Missing required columns: {missing_columns}")
            print("Available columns:", self.data.columns.tolist())
            return False
            
        return True

    def _standardize_column_names(self, T):
        # Original mapping
        mapping = {
            'total-infantry-casualties / 10': 'total_infantry_casualties_10',
            'total-infantry-crossed': 'total_infantry_crossed',
            'total-infantry-used': 'total_infantry_used',
            'total-pontoons-used': 'total_pontoons_used',
            'site-selection-mode': 'site_selection_mode',
            'battle-outcome': 'battle_outcome'
        }
        
        # Apply renaming only for columns that exist
        mapping_to_use = {k: v for k, v in mapping.items() if k in T.columns}
        
        if not mapping_to_use:
            print("Warning: None of the expected columns found for renaming.")
            
        return T.rename(columns=mapping_to_use)

    def _inspect_csv_files(self, file_paths):
        for i, file_path in enumerate(file_paths, 1):
            try:
                print(f"\nFile {i} content check:")
                # Try to read with different skiprows values
                for skip in [0, 1, 6]:
                    print(f"\nTrying with skiprows={skip}:")
                    try:
                        df = pd.read_csv(file_path, skiprows=skip, nrows=5)
                        print(f"First {min(5, len(df))} rows:")
                        print(df.head())
                        print("\nColumns:")
                        print(df.columns.tolist())
                    except Exception as e:
                        print(f"Failed with skiprows={skip}: {e}")
                
                # Also show raw file content
                print("\nRaw file content (first 10 lines):")
                with open(file_path, 'r', encoding='utf-8') as f:
                    for j, line in enumerate(f):
                        if j < 10:
                            print(f"Line {j+1}: {line.strip()}")
                        else:
                            break
            except Exception as e:
                print(f"Failed to read file {i}: {e}")
    
    def calculate_statistics(self):
        """Calculate basic statistical information (converted from MATLAB code)"""
        if self.data is None:
            print("Data not loaded. Please run preprocess_csv_files() first.")
            return False
            
        print("Calculating basic statistics...")
        
        # Ensure required columns exist
        required_columns = ['site_selection_mode', 'battle_outcome', 
                           'total_infantry_casualties_10', 'total_infantry_used']
        
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            print(f"Error: Missing required columns for statistics calculation: {missing_columns}")
            return False
        
        # Get unique site selection modes and battle outcomes
        site_modes = self.data['site_selection_mode'].unique()
        battle_outcomes = self.data['battle_outcome'].unique()
        
        if len(site_modes) == 0:
            print("Warning: No unique site selection modes found")
            return False
            
        print(f"Found site selection modes: {site_modes}")
        print(f"Found battle outcomes: {battle_outcomes}")
        
        # Calculate win rate for each site selection mode
        win_rate = {}
        for mode in site_modes:
            idx = self.data['site_selection_mode'] == mode
            if idx.sum() > 0:  # Ensure we have data for this mode
                victories = self.data[idx]['battle_outcome'] == 'Victory'
                win_rate[mode] = (victories.sum() / idx.sum()) * 100
            else:
                win_rate[mode] = 0
        
        # Calculate casualty rate for each site selection mode
        casualty_rate = {}
        for mode in site_modes:
            idx = self.data['site_selection_mode'] == mode
            if idx.sum() > 0:
                total_casualties = self.data.loc[idx, 'total_infantry_casualties_10'].sum()
                total_used = self.data.loc[idx, 'total_infantry_used'].sum()
                if total_used > 0:
                    casualty_rate[mode] = (total_casualties / total_used) * 100
                else:
                    casualty_rate[mode] = 0
            else:
                casualty_rate[mode] = 0
        
        # Calculate casualty rate for each row
        row_casualty_rate = (self.data['total_infantry_casualties_10'] / self.data['total_infantry_used']) * 100
        
        # Check if 'ticks' column exists for sorting
        if 'ticks' in self.data.columns:
            # Sort by ticks
            sorted_indices = self.data['ticks'].argsort()
            sorted_ticks = self.data['ticks'].iloc[sorted_indices]
            sorted_used = self.data['total_infantry_used'].iloc[sorted_indices]
            sorted_crossed = self.data['total_infantry_crossed'].iloc[sorted_indices] if 'total_infantry_crossed' in self.data.columns else pd.Series([0] * len(sorted_indices))
            sorted_casualties = self.data['total_infantry_casualties_10'].iloc[sorted_indices]
            
            cum_used = np.cumsum(sorted_used)
            cum_crossed = np.cumsum(sorted_crossed)
            cum_casualties = np.cumsum(sorted_casualties)
            
            sorted_data = {
                'ticks': sorted_ticks,
                'used': sorted_used,
                'crossed': sorted_crossed,
                'casualties': sorted_casualties,
                'cum_used': cum_used,
                'cum_crossed': cum_crossed,
                'cum_casualties': cum_casualties
            }
        else:
            print("Warning: 'ticks' column not found, skipping time-based analysis")
            sorted_data = {}
        
        # Calculate mean and median of key metrics for each site selection mode
        mean_used = {}
        median_used = {}
        mean_crossed = {}
        median_crossed = {}
        mean_casualties = {}
        median_casualties = {}
        
        for mode in site_modes:
            idx = self.data['site_selection_mode'] == mode
            
            if idx.sum() > 0:
                mean_used[mode] = self.data.loc[idx, 'total_infantry_used'].mean()
                median_used[mode] = self.data.loc[idx, 'total_infantry_used'].median()
                
                if 'total_infantry_crossed' in self.data.columns:
                    mean_crossed[mode] = self.data.loc[idx, 'total_infantry_crossed'].mean()
                    median_crossed[mode] = self.data.loc[idx, 'total_infantry_crossed'].median()
                
                mean_casualties[mode] = self.data.loc[idx, 'total_infantry_casualties_10'].mean()
                median_casualties[mode] = self.data.loc[idx, 'total_infantry_casualties_10'].median()
            else:
                mean_used[mode] = median_used[mode] = 0
                mean_crossed[mode] = median_crossed[mode] = 0
                mean_casualties[mode] = median_casualties[mode] = 0
            
        # Calculate sum values for each site selection mode
        sum_used = {}
        sum_crossed = {}
        sum_casualties = {}
        
        for mode in site_modes:
            idx = self.data['site_selection_mode'] == mode
            
            if idx.sum() > 0:
                sum_used[mode] = self.data.loc[idx, 'total_infantry_used'].sum()
                
                if 'total_infantry_crossed' in self.data.columns:
                    sum_crossed[mode] = self.data.loc[idx, 'total_infantry_crossed'].sum()
                else:
                    sum_crossed[mode] = 0
                    
                sum_casualties[mode] = self.data.loc[idx, 'total_infantry_casualties_10'].sum()
            else:
                sum_used[mode] = sum_crossed[mode] = sum_casualties[mode] = 0
            
        # Store statistics in the dictionary
        self.statistics = {
            'site_modes': site_modes,
            'battle_outcomes': battle_outcomes,
            'win_rate': win_rate,
            'casualty_rate': casualty_rate,
            'row_casualty_rate': row_casualty_rate,
            'sorted_data': sorted_data,
            'mean': {
                'used': mean_used,
                'crossed': mean_crossed,
                'casualties': mean_casualties
            },
            'median': {
                'used': median_used,
                'crossed': median_crossed,
                'casualties': median_casualties
            },
            'sum': {
                'used': sum_used,
                'crossed': sum_crossed,
                'casualties': sum_casualties
            }
        }
        
        print("Basic statistics calculation completed.")
        return True
    
    
    
       
    def create_boxplots(self):
        """Create box plots for success ratio and casualty ratio by site selection mode"""
        if self.data is None or not self.statistics:
            print("Data or statistics not available. Please run preprocess_csv_files and calculate_statistics first.")
            return
            
        print("Creating boxplots for success and casualty ratios...")
        
        # Calculate row-wise success indicator (1 for Victory, 0 for Retreat)
        self.data['success'] = (self.data['battle_outcome'] == 'Victory').astype(int) * 100
        
        # Calculate row-wise casualty ratio
        self.data['casualty_ratio'] = (self.data['total_infantry_casualties_10'] / self.data['total_infantry_used']) * 100
        
        # Set figure style
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Box plot for success ratio
        sns.boxplot(x='site_selection_mode', y='success', data=self.data, ax=ax1, palette='YlGn')
        ax1.set_title('Success Ratio by Site Selection Mode', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Site Selection Mode', fontsize=14)
        ax1.set_ylabel('Success Ratio (%)', fontsize=14)
        ax1.set_ylim(-5, 105)
        
        # Box plot for casualty ratio
        sns.boxplot(x='site_selection_mode', y='casualty_ratio', data=self.data, ax=ax2, palette='YlOrRd')
        ax2.set_title('Casualty Ratio by Site Selection Mode', fontsize=16, fontweight='bold')
        ax2.set_xlabel('Site Selection Mode', fontsize=14)
        ax2.set_ylabel('Casualty Ratio (%)', fontsize=14)
        
        # Rotate x-axis labels
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save the figure
        output_file = os.path.join(self.output_dir, "Site_Selection_Boxplots.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Boxplots saved to {output_file}")
        
        plt.show()
    
    def create_combined_bar_chart(self):
        """Create a combined bar chart showing success ratio and casualty ratio by site selection mode"""
        if not self.statistics:
            print("Statistics not available. Please run calculate_statistics first.")
            return
            
        print("Creating combined bar chart for success and casualty ratios...")
        
        # Prepare the data
        site_modes = self.statistics['site_modes']
        win_rates = [self.statistics['win_rate'][mode] for mode in site_modes]
        casualty_rates = [self.statistics['casualty_rate'][mode] for mode in site_modes]
        
        # Set up the figure
        plt.figure(figsize=(14, 8))
        
        # Set bar positions
        x = np.arange(len(site_modes))
        width = 0.35
        
        # Create bars
        plt.bar(x - width/2, win_rates, width, label='Success Rate', color='#2ecc71', edgecolor='black')
        plt.bar(x + width/2, casualty_rates, width, label='Casualty Rate', color='#e74c3c', edgecolor='black')
        
        # Add labels and title
        plt.xlabel('Site Selection Mode', fontsize=14, fontweight='bold')
        plt.ylabel('Percentage (%)', fontsize=14, fontweight='bold')
        plt.title('Success Rate and Casualty Rate by Site Selection Mode', fontsize=16, fontweight='bold')
        
        # Add data labels on bars
        for i, v in enumerate(win_rates):
            plt.text(i - width/2, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
            
        for i, v in enumerate(casualty_rates):
            plt.text(i + width/2, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
        
        # Customize x-axis
        plt.xticks(x, site_modes, rotation=45, ha='right')
        
        # Add legend
        plt.legend()
        
        # Add grid
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Save the figure
        output_file = os.path.join(self.output_dir, "Site_Selection_Combined_Bar_Chart.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Combined bar chart saved to {output_file}")
        
        plt.show()
    

    
    def create_visualizations(self):
        """Create all visualizations at once"""
        if not self.statistics:
            print("Statistics not available. Please run calculate_statistics first.")
            return False
            
        print("Creating all visualizations...")
        
        # Create boxplots
        self.create_boxplots()
        
        # Create combined bar chart
        self.create_combined_bar_chart()
        
        print("All visualizations completed.")
        return True
    
    
    
    
def main():
    """Main function to execute the analysis."""
    print("Starting Irpin River battle data analysis...")
    
    # Initialize the analyzer
    analyzer = IrpinDataAnalyzer()
    
    # Preprocess the data - explicitly specify the table file
    table_file = os.path.join(analyzer.output_dir, "IrpinModel Vary Site-Selection Artillery Active-table.csv")
    if analyzer.preprocess_csv_files(table_file):
        # Calculate statistics
        if analyzer.calculate_statistics():
            # Generate all visualizations
            analyzer.create_visualizations()
            print("Analysis completed successfully.")
        else:
            print("Analysis failed during statistics calculation.")
    else:
        print("Analysis failed due to data loading issues.")

if __name__ == '__main__':
    main()